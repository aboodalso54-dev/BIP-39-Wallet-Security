package com.example.myapp

import android.graphics.Color
import android.graphics.Typeface
import android.os.Bundle
import android.text.InputType
import android.view.ViewGroup
import android.widget.Button
import android.widget.EditText
import android.widget.LinearLayout
import android.widget.ScrollView
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import kotlin.concurrent.thread

class MainActivity : AppCompatActivity() {

    private lateinit var output: TextView
    private lateinit var mnemonicInput: EditText
    private lateinit var passphraseInput: EditText
    private var entropyBits = 128

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        Bip39.loadWordlist(this)
        setContentView(buildUi())
        generate()
    }

    private fun dp(value: Int) = (value * resources.displayMetrics.density).toInt()

    private fun label(text: String, size: Float = 16f, bold: Boolean = false) = TextView(this).apply {
        this.text = text
        textSize = size
        setTextColor(Color.parseColor("#0F172A"))
        if (bold) setTypeface(Typeface.DEFAULT_BOLD)
        setPadding(0, dp(4), 0, dp(4))
    }

    private fun mono(text: String, size: Float = 13f) = TextView(this).apply {
        this.text = text
        textSize = size
        typeface = Typeface.MONOSPACE
        setTextColor(Color.parseColor("#0F766E"))
        setBackgroundColor(Color.parseColor("#F1F5F9"))
        setPadding(dp(12), dp(12), dp(12), dp(12))
        setTextIsSelectable(true)
    }

    private fun buildUi(): ViewGroup {
        val root = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setBackgroundColor(Color.parseColor("#FFFFFF"))
            setPadding(dp(20), dp(24), dp(20), dp(24))
        }

        root.addView(label("BIP-39 Wallet Security & Entropy Simulator", 20f, bold = true))
        root.addView(label(
            "توليد entropy عشوائي، تحويله إلى mnemonicphrase، اشتقاق الـ seed، " +
                "تقدير زمن كسر الحماية brute-force.", 13f
        ))

        root.addView(label("\nEntropy (bits)", 15f, bold = true))
        val bitsRow = LinearLayout(this).apply { orientation = LinearLayout.HORIZONTAL }
        Bip39.supportedEntropyBits().forEach { bits ->
            bitsRow.addView(Button(this).apply {
                text = "$bits"
                isAllCaps = false
                setOnClickListener {
                    entropyBits = bits
                    generate()
                }
            }, LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.WRAP_CONTENT, 1f))
        }
        root.addView(bitsRow)

        passphraseInput = EditText(this).apply {
            hint = "Passphrase (اختياري)"
            inputType = InputType.TYPE_CLASS_TEXT
        }
        root.addView(passphraseInput)

        root.addView(Button(this).apply {
            text = "توليد mnemonic جديد"
            setOnClickListener { generate() }
        }, LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT).apply {
            topMargin = dp(12)
        })

        output = TextView(this).apply {
            typeface = Typeface.MONOSPACE
            textSize = 12f
            setPadding(0, dp(16), 0, 0)
        }
        root.addView(output)

        root.addView(label("\nفحص / اشتقاق mnemonicphrase مُدخل", 15f, bold = true))
        mnemonicInput = EditText(this).apply {
            hint = "أدخل 12 أو 24 كلمة مفصولة بمسافات"
            inputType = InputType.TYPE_CLASS_TEXT or InputType.TYPE_TEXT_FLAG_MULTI_LINE
            minLines = 2
            setTextIsSelectable(true)
        }
        root.addView(mnemonicInput)
        root.addView(Button(this).apply {
            text = "تحقّق واشتقاق seed"
            setOnClickListener { validateAndDerive() }
        })

        val scroll = ScrollView(this)
        scroll.addView(root)
        return scroll
    }

    private fun generate() {
        val passphrase = passphraseInput.text.toString()
        thread(name = "bip39-generate") {
            val result = Bip39.generate(entropyBits, passphrase)
            val wordsPerLine = 4
            val grouped = result.words.chunked(wordsPerLine).joinToString("\n") { it.joinToString("  ") }
            val text = buildString {
                append("Entropy: ${result.entropyHex}\n")
                append("Bits: ${result.entropyBits}  |  Checksum: ${result.checksumBits} bit\n")
                append("Mnemonic (${result.words.size} كلمة):\n\n")
                append(grouped)
                append("\n\nSeed (PBKDF2-HMAC-SHA512, ${Bip39.PBKDF2_ITERATIONS} دورة):\n")
                append(result.seedHex.chunked(32).joinToString("\n"))
                append("\n\nBrute-force عند 10^12 محاولة/ثانية:\n")
                append("2^${result.entropyBits} = ")
                append("%.3e".format(Math.pow(2.0, result.entropyBits.toDouble())))
                append(" Keys → ")
                append(Bip39.bruteForceEstimate(result.entropyBits))
                append("\nعالميًا (10^18/ثانية): ")
                append(Bip39.bruteForceEstimate(result.entropyBits, 1e18))
            }
            runOnUiThread { output.text = text }
        }
    }

    private fun validateAndDerive() {
        val words = mnemonicInput.text.toString().trim().split(Regex("\\s+")).filter { it.isNotEmpty() }
        val passphrase = passphraseInput.text.toString()
        thread(name = "bip39-validate") {
            val validation = Bip39.validate(words)
            val text = if (validation.startsWith("✅")) {
                val entropy = Bip39.mnemonicToEntropy(words)
                val seed = Bip39.toSeed(words, passphrase)
                buildString {
                    append(validation).append("\n\n")
                    append("Entropy: ").append(entropy.joinToString("") { "%02x".format(it) }).append("\n")
                    append("Seed:\n").append(seed.joinToString("") { "%02x".format(it) }.chunked(32).joinToString("\n"))
                    append("\n\nزمن كسر 2^").append(entropy.size * 8).append(": ")
                    append(Bip39.bruteForceEstimate(entropy.size * 8))
                }
            } else {
                validation
            }
            runOnUiThread {
                output.text = text
                mnemonicInput.setText(words.joinToString(" ") { it.lowercase() })
            }
        }
    }
}