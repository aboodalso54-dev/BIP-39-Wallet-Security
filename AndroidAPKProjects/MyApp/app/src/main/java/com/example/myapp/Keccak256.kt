package com.example.myapp

/**
 * Keccak-256 (original padding, used by Ethereum) — not the same as SHA3-256.
 * Verified against the official SHA3-256 test vectors when padding is switched to 0x06.
 */
object Keccak256 {

    private val ROUND_CONSTANTS = longArrayOf(
        0x0000000000000001uL.toLong(), 0x0000000000008082uL.toLong(), 0x800000000000808AuL.toLong(),
        0x8000000080008000uL.toLong(), 0x000000000000808BuL.toLong(), 0x0000000080000001uL.toLong(),
        0x8000000080008081uL.toLong(), 0x8000000000008009uL.toLong(), 0x000000000000008AuL.toLong(),
        0x0000000000000088uL.toLong(), 0x0000000080008009uL.toLong(), 0x000000008000000AuL.toLong(),
        0x000000008000808BuL.toLong(), 0x800000000000008BuL.toLong(), 0x8000000000008089uL.toLong(),
        0x8000000000008003uL.toLong(), 0x8000000000008002uL.toLong(), 0x8000000000000080uL.toLong(),
        0x000000000000800AuL.toLong(), 0x800000008000000AuL.toLong(), 0x8000000080008081uL.toLong(),
        0x8000000000008080uL.toLong(), 0x0000000080000001uL.toLong(), 0x8000000080008008uL.toLong()
    )

    private val ROTATION = arrayOf(
        intArrayOf(0, 36, 3, 41, 18),
        intArrayOf(1, 44, 10, 45, 2),
        intArrayOf(62, 6, 43, 15, 61),
        intArrayOf(28, 55, 25, 21, 56),
        intArrayOf(27, 20, 39, 8, 14)
    )

    private const val RATE = 136

    fun digest(input: ByteArray): ByteArray {
        val padded = input.toMutableList()
        padded.add(0x01)
        while (padded.size % RATE != 0) padded.add(0)
        padded[padded.size - 1] = (padded[padded.size - 1].toInt() or 0x80).toByte()

        val state = LongArray(25)
        for (offset in padded.indices step RATE) {
            for (i in 0 until RATE / 8) {
                var lane = 0L
                for (b in 7 downTo 0) lane = (lane shl 8) or (padded[offset + i * 8 + b].toLong() and 0xFF)
                state[i] = state[i] xor lane
            }
            permute(state)
        }

        val out = ByteArray(32)
        for (i in 0 until 4) {
            var lane = state[i]
            for (b in 0 until 8) {
                out[i * 8 + b] = (lane and 0xFF).toByte()
                lane = lane ushr 8
            }
        }
        return out
    }

    private fun permute(a: LongArray) {
        for (round in 0 until 24) {
            val c = LongArray(5)
            for (x in 0 until 5) c[x] = a[x] xor a[x + 5] xor a[x + 10] xor a[x + 15] xor a[x + 20]
            val d = LongArray(5)
            for (x in 0 until 5) d[x] = c[(x + 4) % 5] xor java.lang.Long.rotateLeft(c[(x + 1) % 5], 1)

            for (x in 0 until 5) for (y in 0 until 5) a[x + 5 * y] = a[x + 5 * y] xor d[x]

            val b = LongArray(25)
            for (x in 0 until 5) {
                for (y in 0 until 5) {
                    b[y + 5 * ((2 * x + 3 * y) % 5)] =
                        java.lang.Long.rotateLeft(a[x + 5 * y], ROTATION[x][y])
                }
            }

            for (x in 0 until 5) {
                for (y in 0 until 5) {
                    a[x + 5 * y] = b[x + 5 * y] xor (b[(x + 1) % 5 + 5 * y].inv() and b[(x + 2) % 5 + 5 * y])
                }
            }

            a[0] = a[0] xor ROUND_CONSTANTS[round]
        }
    }
}