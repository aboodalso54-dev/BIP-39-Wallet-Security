package com.example.myapp

import java.math.BigInteger

/** Minimal secp256k1 implementation: point arithmetic and public key derivation. */
object Secp256k1 {

    val P = BigInteger("FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F", 16)
    val N = BigInteger("FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141", 16)
    val Gx = BigInteger("79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798", 16)
    val Gy = BigInteger("483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8", 16)

    class Point(val x: BigInteger, val y: BigInteger)

    private val ZERO: Point? = null

    private fun addPoint(a: Point?, b: Point?): Point? {
        if (a == null) return b
        if (b == null) return a
        if (a.x == b.x && a.y.add(b.y).mod(P).signum() == 0) return ZERO
        val lambda = if (a == b) {
            val num = a.x.multiply(a.x).multiply(BigInteger.valueOf(3))
            val den = a.y.multiply(BigInteger.valueOf(2)).modInverse(P)
            num.multiply(den).mod(P)
        } else {
            val num = b.y.subtract(a.y).mod(P)
            val den = b.x.subtract(a.x).mod(P).modInverse(P)
            num.multiply(den).mod(P)
        }
        val x = lambda.multiply(lambda).subtract(a.x).subtract(b.x).mod(P)
        val y = lambda.multiply(a.x.subtract(x)).subtract(a.y).mod(P)
        return Point(x, y)
    }

    fun publicKey(privateKey: BigInteger): Point {
        require(privateKey.signum() > 0 && privateKey < N) { "Private key out of range" }
        var result: Point? = ZERO
        var base = Point(Gx, Gy)
        var k = privateKey
        while (k.signum() > 0) {
            if (k.testBit(0)) result = addPoint(result, base)
            base = addPoint(base, base)!!
            k = k.shiftRight(1)
        }
        return requireNotNull(result) { "Invalid point" }
    }

    fun compressed(point: Point): ByteArray {
        val prefix = if (point.y.testBit(0)) 0x03.toByte() else 0x02.toByte()
        return byteArrayOf(prefix) + point.x.toFixed32()
    }

    fun uncompressed(point: Point): ByteArray =
        byteArrayOf(0x04) + point.x.toFixed32() + point.y.toFixed32()

    fun BigInteger.toFixed32(): ByteArray {
        val raw = toByteArray()
        return if (raw.size == 32) raw else if (raw.size < 32) ByteArray(32 - raw.size) + raw else raw.copyOfRange(raw.size - 32, raw.size)
    }
}