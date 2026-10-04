package com.example.myapp

import java.math.BigInteger
import java.security.MessageDigest
import javax.crypto.Mac
import javax.crypto.spec.SecretKeySpec

data class DerivedAccount(
    val path: String,
    val privateKeyHex: String,
    val publicKeyHex: String,
    val ethAddress: String,
    val btcAddress: String,
    val xprv: String,
    val xpub: String
)

/** BIP-32 hierarchical deterministic key derivation with BIP-44 paths. */
object Bip32 {

    private val HARDENED_BIT = 0x80000000L

    private fun hmac512(key: ByteArray, data: ByteArray): ByteArray {
        val mac = Mac.getInstance("HmacSHA512")
        mac.init(SecretKeySpec(key, "HmacSHA512"))
        return mac.doFinal(data)
    }

    fun hash160(data: ByteArray): ByteArray {
        val sha = MessageDigest.getInstance("SHA-256").digest(data)
        return MessageDigest.getInstance("RIPEMD160").digest(sha)
    }

    /** RIPEMD-160 is available on Android but not on all desktop JVMs. */
    private fun base58P2pkhOrNull(publicKey: ByteArray): String? = try {
        base58Check(byteArrayOf(0x00) + hash160(publicKey))
    } catch (e: java.security.NoSuchAlgorithmException) {
        null
    }

    fun toFixed32(value: BigInteger): ByteArray = Secp256k1.run { value.toFixed32() }

    private fun deriveChild(key: ByteArray, chainCode: ByteArray, index: Long): Pair<ByteArray, ByteArray> {
        val indexBytes = byteArrayOf(
            ((index ushr 24) and 0xFF).toByte(),
            ((index ushr 16) and 0xFF).toByte(),
            ((index ushr 8) and 0xFF).toByte(),
            (index and 0xFF).toByte()
        )
        val data = if (index >= HARDENED_BIT) {
            byteArrayOf(0) + key + indexBytes
        } else {
            Secp256k1.compressed(Secp256k1.publicKey(BigInteger(1, key))) + indexBytes
        }
        val i = hmac512(chainCode, data)
        val childKey = BigInteger(1, i.copyOfRange(0, 32)).add(BigInteger(1, key)).mod(Secp256k1.N)
        return toFixed32(childKey) to i.copyOfRange(32, 64)
    }

    /** Derives the key at [path] (e.g. m/44'/60'/0'/0/0) from a BIP-39 seed. */
    fun derive(seed: ByteArray, path: String): Pair<ByteArray, ByteArray> {
        val i = hmac512("Bitcoin seed".toByteArray(Charsets.UTF_8), seed)
        var key = i.copyOfRange(0, 32)
        var chainCode = i.copyOfRange(32, 64)
        for (segment in path.trim('/').split('/').drop(1)) {
            val hardened = segment.endsWith("'") || segment.endsWith("h")
            val number = segment.trimEnd('\'', 'h').toInt()
            val index = if (hardened) number + HARDENED_BIT else number.toLong()
            val child = deriveChild(key, chainCode, index)
            key = child.first
            chainCode = child.second
        }
        return key to chainCode
    }

    fun account(seed: ByteArray, path: String): DerivedAccount {
        val (key, chainCode) = derive(seed, path)
        val point = Secp256k1.publicKey(BigInteger(1, key))
        val uncompressed = Secp256k1.uncompressed(point)
        val publicKey = Secp256k1.compressed(point)
        val ethHash = Keccak256.digest(uncompressed.copyOfRange(1, 65))
        val eth = "0x" + ethHash.copyOfRange(12, 32).joinToString("") { "%02x".format(it) }
        val btc = base58P2pkhOrNull(publicKey) ?: "غير متاح (RIPEMD-160 غير مدعوم)"

        val privateKey = BigInteger(1, key)
        val pubPoint = Secp256k1.publicKey(privateKey)
        val xprv = base58Check(
            byteArrayOf(0x04, 0x88.toByte(), 0xAD.toByte(), 0xE4.toByte()) + toFixed32(privateKey) + chainCode + byteArrayOf(0)
        )
        val xpub = base58Check(
            byteArrayOf(0x04, 0x88.toByte(), 0xB2.toByte(), 0x1E.toByte()) + Secp256k1.compressed(pubPoint) + chainCode + byteArrayOf(0)
        )

        return DerivedAccount(
            path = path,
            privateKeyHex = key.joinToString("") { "%02x".format(it) },
            publicKeyHex = publicKey.joinToString("") { "%02x".format(it) },
            ethAddress = eth,
            btcAddress = btc,
            xprv = xprv,
            xpub = xpub
        )
    }

    fun ethAccount(seed: ByteArray, accountIndex: Int = 0, change: Int = 0, addressIndex: Int = 0) =
        account(seed, "m/44'/60'/0'/$change/$addressIndex")

    fun btcAccount(seed: ByteArray, accountIndex: Int = 0, change: Int = 0, addressIndex: Int = 0) =
        account(seed, "m/44'/0'/0'/$change/$addressIndex")

    private val BASE58 = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"

    fun base58Check(payload: ByteArray): String {
        val checksum = MessageDigest.getInstance("SHA-256")
            .digest(MessageDigest.getInstance("SHA-256").digest(payload))
            .copyOfRange(0, 4)
        return base58Encode(payload + checksum)
    }

    private fun base58Encode(bytes: ByteArray): String {
        if (bytes.isEmpty()) return ""
        val alphabet = BASE58
        var leadingZeros = 0
        while (leadingZeros < bytes.size && bytes[leadingZeros].toInt() == 0) leadingZeros++
        val value = BigInteger(1, bytes)
        val radix = BigInteger.valueOf(58)
        val digits = StringBuilder()
        var current = value
        while (current.signum() > 0) {
            val (quotient, remainder) = current.divideAndRemainder(radix)
            digits.append(alphabet[remainder.toInt()])
            current = quotient
        }
        return "1".repeat(leadingZeros) + digits.reverse()
    }
}