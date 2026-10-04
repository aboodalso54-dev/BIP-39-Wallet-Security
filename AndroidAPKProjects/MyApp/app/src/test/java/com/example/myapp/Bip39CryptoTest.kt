package com.example.myapp

import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Before
import org.junit.Test
import java.io.File
import java.math.BigInteger

class Bip39CryptoTest {

    private val entropyHex = "00000000000000000000000000000000"

    @Before
    fun loadWordlist() {
        val candidates = listOf(
            File("src/main/assets/bip39/english.txt"),
            File("app/src/main/assets/bip39/english.txt")
        )
        val file = candidates.firstOrNull { it.exists() }
            ?: error("wordlist asset not found in ${File(".").absolutePath}")
        Bip39.loadWordlistFrom(file.inputStream())
    }

    @Test
    fun `keccak256 matches known vectors`() {
        assertEquals(
            "c5d2460186f7233c927e7db2dcc703c0e500b653ca82273b7bfad8045d85a470",
            Keccak256.digest(ByteArray(0)).joinToString("") { "%02x".format(it) }
        )
        assertEquals(
            "4e03657aea45a94fc7d47ba826c8d667c0d1e6e33a64a036ec44f58fa12d6c45",
            Keccak256.digest("abc".toByteArray()).joinToString("") { "%02x".format(it) }
        )
    }

    @Test
    fun `secp256k1 generator point and address of private key one`() {
        val point = Secp256k1.publicKey(BigInteger.ONE)
        assertEquals(
            "0279be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798",
            Secp256k1.compressed(point).joinToString("") { "%02x".format(it) }
        )
        val address = Keccak256.digest(Secp256k1.uncompressed(point).copyOfRange(1, 65))
            .copyOfRange(12, 32).joinToString("") { "%02x".format(it) }
        assertEquals("7e5f4552091a69125d5dfcb7b8c2659029395bdf", address)
    }

    @Test
    fun `bip39 seed derivation matches reference`() {
        val mnemonic = "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about"
        val seed = Bip39.toSeed(mnemonic.split(" "))
        assertEquals(
            "5eb00bbddcf069084889a8ab9155568165f5c453ccb85e70811aaed6f6da5fc1" +
                "9a5ac40b389cd370d086206dec8aa6c43daea6690f20ad3d8d48b2d2ce9e38e4",
            seed.joinToString("") { "%02x".format(it) }
        )
    }

    @Test
    fun `bip32 matches official test vector 1`() {
        val seed = hexToBytes("000102030405060708090a0b0c0d0e0f")
        val (rootKey, rootChain) = Bip32.derive(seed, "m")
        assertEquals(
            "e8f32e723decf4051aefac8e2c93c9c5b214313817cdb01a1494b917c8436b35",
            rootKey.joinToString("") { "%02x".format(it) }
        )
        assertEquals(
            "873dff81c02f525623fd1fe5167eac3a55a049de3d314bb42ee227ffed37d508",
            rootChain.joinToString("") { "%02x".format(it) }
        )

        val (second, _) = Bip32.derive(seed, "m/0'")
        assertEquals(
            "edb2e14f9ee77d26dd93b4ecede8d16ed408ce149b6cd80b0715a2d911a0afea",
            second.joinToString("") { "%02x".format(it) }
        )

        val (deep, _) = Bip32.derive(seed, "m/0'/1/2'/2/1000000000")
        assertEquals(
            "471b76e389e528d6de6d816857e012c5455051cad6660850e58372a6c3e6e7c8",
            deep.joinToString("") { "%02x".format(it) }
        )
    }

    @Test
    fun `ethereum address matches well known test mnemonic`() {
        val mnemonic = "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about"
        val account = Bip32.ethAccount(Bip39.toSeed(mnemonic.split(" ")))
        assertEquals("m/44'/60'/0'/0/0", account.path)
        assertEquals("0x9858effd232b4033e47d90003d41ec34ecaeda94", account.ethAddress)
    }

    @Test
    fun `hardhat development account matches`() {
        val mnemonic = "test test test test test test test test test test test junk"
        val account = Bip32.ethAccount(Bip39.toSeed(mnemonic.split(" ")))
        assertEquals("0xf39fd6e51aad88f6f4ce6ab8827279cfffb92266", account.ethAddress)
        assertEquals(
            "ac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80",
            account.privateKeyHex
        )
    }

    @Test
    fun `mnemonic round trips and rejects tampering`() {
        val entropy = hexToBytes(entropyHex)
        val (words, checksumBits) = Bip39.toMnemonic(entropy)
        assertEquals(12, words.size)
        assertEquals(4, checksumBits)
        assertTrue(entropy.contentEquals(Bip39.mnemonicToEntropy(words)))
        assertTrue(Bip39.validate(words).startsWith("✅"))

        val tampered = words.toMutableList()
        tampered[3] = if (tampered[3] == "zoo") "zone" else "zoo"
        assertTrue(Bip39.validate(tampered).startsWith("❌"))
    }

    private fun hexToBytes(hex: String): ByteArray =
        hex.chunked(2).map { it.toInt(16).toByte() }.toByteArray()
}