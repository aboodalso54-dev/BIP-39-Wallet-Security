package com.example.myapp

import android.content.Context
import java.security.MessageDigest
import java.security.SecureRandom
import javax.crypto.Mac
import javax.crypto.SecretKeyFactory
import javax.crypto.spec.PBEKeySpec

data class Bip39Result(
    val entropyHex: String,
    val entropyBits: Int,
    val words: List<String>,
    val checksumBits: Int,
    val seedHex: String
)

object Bip39 {

    const val PBKDF2_ITERATIONS = 2048

    private var cachedWordlist: List<String>? = null

    /** Loads the official 2048-word list from assets. Must be called once before any other method. */
    fun loadWordlist(context: Context) {
        if (cachedWordlist != null) return
        loadWordlistFrom(context.assets.open("bip39/english.txt"))
    }

    /** Loads the wordlist from any stream (assets on device, classpath in unit tests). */
    fun loadWordlistFrom(stream: java.io.InputStream) {
        if (cachedWordlist != null) return
        val words = stream.bufferedReader().useLines { lines ->
            lines.map { it.trim() }.filter { it.isNotEmpty() }.toList()
        }
        require(words.size == 2048) { "Wordlist must contain 2048 words, found ${words.size}" }
        cachedWordlist = words
    }

    private val WORDLIST: List<String>
        get() = cachedWordlist ?: error("Bip39.loadWordlist(context) must be called first")

    fun supportedEntropyBits() = intArrayOf(128, 160, 192, 224, 256)

    fun generateEntropy(bits: Int): ByteArray {
        require(bits in supportedEntropyBits()) { "Entropy must be 128-256 bits in steps of 32" }
        val bytes = ByteArray(bits / 8)
        SecureRandom().nextBytes(bytes)
        return bytes
    }

    private fun entropyToBinary(bytes: ByteArray): String =
        bytes.joinToString("") { byteToBinary(it) }

    private fun byteToBinary(byte: Byte): String =
        Integer.toBinaryString(byte.toInt() and 0xFF).padStart(8, '0')

    fun toMnemonic(entropy: ByteArray): Pair<List<String>, Int> {
        val entropyBits = entropy.size * 8
        val checksumBits = entropyBits / 32
        val checksum = sha256(entropy)
        val checksumBinary = byteToBinary(checksum[0]).take(checksumBits)
        val binary = entropyToBinary(entropy) + checksumBinary
        return binary.chunked(11).map { WORDLIST[it.toInt(2)] } to checksumBits
    }

    fun mnemonicToEntropy(words: List<String>): ByteArray {
        require(words.size in 12..24 && words.size % 3 == 0) { "Mnemonic must have 12, 15, 18, 21 or 24 words" }
        val bits = words.joinToString("") { word ->
            val index = WORDLIST.indexOf(word.lowercase())
            require(index >= 0) { "Unknown word: $word" }
            Integer.toBinaryString(index).padStart(11, '0')
        }
        val entropyBits = bits.length * 32 / 33
        val checksumBits = entropyBits / 32
        val entropyBinary = bits.substring(0, entropyBits)
        val checksumBinary = bits.substring(entropyBits)
        val entropy = entropyBinary.chunked(8).map { it.toInt(2).toByte() }.toByteArray()
        val expected = byteToBinary(sha256(entropy)[0]).take(checksumBits)
        require(expected == checksumBinary) { "Checksum mismatch — a word was mistyped or altered" }
        return entropy
    }

    fun toSeed(words: List<String>, passphrase: String = ""): ByteArray {
        val mnemonic = words.joinToString(" ") { it.lowercase() }
        val salt = "mnemonic$passphrase"
        // BIP-39: PBKDF2-HMAC-SHA512, password = mnemonic (NFKD UTF-8), salt = "mnemonic" + passphrase
        val spec = PBEKeySpec(
            mnemonic.toCharArray(),
            salt.toByteArray(Charsets.UTF_8),
            PBKDF2_ITERATIONS,
            512
        )
        return SecretKeyFactory.getInstance("PBKDF2WithHmacSHA512").generateSecret(spec).encoded
    }

    fun generate(bits: Int, passphrase: String = ""): Bip39Result {
        val entropy = generateEntropy(bits)
        val (words, checksumBits) = toMnemonic(entropy)
        return Bip39Result(
            entropyHex = entropy.joinToString("") { "%02x".format(it) },
            entropyBits = bits,
            words = words,
            checksumBits = checksumBits,
            seedHex = toSeed(words, passphrase).joinToString("") { "%02x".format(it) }
        )
    }

    fun validate(words: List<String>): String {
        return try {
            val entropy = mnemonicToEntropy(words)
            val (rebuilt, _) = toMnemonic(entropy)
            if (rebuilt == words.map { it.lowercase() }) "✅ Valid mnemonic (${words.size} words, ${entropy.size * 8}-bit entropy)"
            else "❌ Checksum valid but words do not round-trip"
        } catch (e: Exception) {
            "❌ ${e.message}"
        }
    }

    /** Universe size = 2^entropyBits; returns human-readable time for a given guess rate. */
    fun bruteForceEstimate(entropyBits: Int, guessesPerSecond: Double = 1e12): String {
        val universe = Math.pow(2.0, entropyBits.toDouble())
        val seconds = universe / guessesPerSecond
        return formatDuration(seconds)
    }

    fun formatDuration(seconds: Double): String {
        if (seconds < 1) return "أقل من ثانية"
        val units = listOf(
            "سنة" to 365.25 * 24 * 3600,
            "يوم" to 24.0 * 3600,
            "ساعة" to 3600.0,
            "دقيقة" to 60.0
        )
        for ((label, factor) in units) {
            if (seconds >= factor) {
                val value = seconds / factor
                return if (value >= 1_000_000) String.format("%.2e", value) + " " + label
                else String.format("%.2f", value) + " " + label
            }
        }
        return String.format("%.2f", seconds) + " ثانية"
    }

    private fun sha256(data: ByteArray): ByteArray = MessageDigest.getInstance("SHA-256").digest(data)
}