"""Unit tests for the PS-P1 Quantum-Safe Secure Channel protocol and backends."""
from __future__ import annotations

import hashlib
import secrets
from pathlib import Path
import pytest

from src.problem import PARAMETER_SETS
from src.process import (
    ClassicalBackend,
    HandshakeError,
    HybridBackend,
    PQCryptoBackend,
    RecordError,
    get_backend,
    make_identity,
    pack,
    run_loopback_transfer,
    tcp_demo,
    unpack,
)


class TestBackends:
    @pytest.mark.parametrize("param_set", ["classical-p256", "pqc-L3", "hybrid-L3"])
    def test_backend_instantiation_and_algorithms(self, param_set: str):
        backend = get_backend(param_set)
        assert backend is not None
        assert backend.kem_alg
        assert backend.sig_alg

    @pytest.mark.parametrize("param_set", ["classical-p256", "pqc-L3", "hybrid-L3"])
    def test_kem_roundtrip(self, param_set: str):
        backend = get_backend(param_set)
        pk, sk = backend.kem_keygen()
        assert len(pk) > 0
        assert len(sk) > 0

        ct, ss_enc = backend.kem_encaps(pk)
        assert len(ct) > 0
        assert len(ss_enc) > 0

        ss_dec = backend.kem_decaps(sk, ct)
        assert ss_enc == ss_dec

    @pytest.mark.parametrize("param_set", ["classical-p256", "pqc-L3", "hybrid-L3"])
    def test_signature_roundtrip(self, param_set: str):
        backend = get_backend(param_set)
        pk, sk = backend.sig_keygen()
        assert len(pk) > 0
        assert len(sk) > 0

        msg = b"quantum-safe audit verification payload"
        sig = backend.sign(sk, msg)
        assert len(sig) > 0
        assert backend.verify(pk, msg, sig) is True
        assert backend.verify(pk, b"tampered message", sig) is False


class TestWireFormat:
    def test_pack_unpack_roundtrip(self):
        f1 = b"hello"
        f2 = b""
        f3 = b"\x00\xff\xfe\x01\x42"
        packed = pack(f1, f2, f3)
        unpacked = unpack(packed, expect=3)
        assert unpacked == [f1, f2, f3]

    def test_unpack_malformed_raises_handshake_error(self):
        with pytest.raises(HandshakeError):
            unpack(b"\x00\x00\x00\x10truncated")


class TestSecureChannelTransfer:
    @pytest.mark.parametrize("param_set", ["classical-p256", "pqc-L3", "hybrid-L3"])
    def test_loopback_transfer_success(self, param_set: str):
        backend = get_backend(param_set)
        client_id = make_identity(backend)
        server_id = make_identity(backend)

        data = [secrets.token_bytes(4096), secrets.token_bytes(512)]
        digest = hashlib.sha256(b"".join(data)).digest()

        result = run_loopback_transfer(backend, client_id, server_id, data, digest)
        assert result.handshake_ok is True
        assert result.payload_ok is True
        assert result.error is None
        assert result.handshake_ms > 0
        assert result.transfer_ms >= 0
        assert result.bytes_total > 0

    @pytest.mark.parametrize("param_set", ["classical-p256", "pqc-L3", "hybrid-L3"])
    def test_tcp_demo_end_to_end(self, param_set: str):
        msg = b"Verified Qiskit Fall Fest 2026 Transmission"
        res = tcp_demo(param_set, message=msg, file=None, chunk_bytes=16384)
        assert res["server_got"] == msg
        assert res["server_ack"].startswith("ack: ")
        assert res["bytes_on_wire"] > 0
