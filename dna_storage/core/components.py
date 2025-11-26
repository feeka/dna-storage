from abc import ABC, abstractmethod
from typing import Iterable, Any


class Inputter(ABC):
    """Abstract inputter - produces a stream/vector of messages (bytes).

    Implementations should yield fixed-size byte messages (or variable size with metadata).
    """

    @abstractmethod
    def read(self) -> Iterable[bytes]:
        """Return an iterable/iterator of message bytes."""


class Encoder(ABC):
    """Abstract encoder that takes a message bytes and produces codewords (as bytes or symbols)."""

    @abstractmethod
    def encode(self, message: bytes) -> Any:
        raise NotImplementedError()


class Mapper(ABC):
    """Maps codewords/symbols to DNA sequences (strings of A/C/G/T)."""

    @abstractmethod
    def map(self, codeword: Any) -> str:
        raise NotImplementedError()


class Channel(ABC):
    """Simulate synthesis/sequencing channel. Input is a list of DNA strands and output is list of reads (with errors).
    """

    @abstractmethod
    def transmit(self, strands: Iterable[str]) -> Iterable[str]:
        raise NotImplementedError()


class Decoder(ABC):
    @abstractmethod
    def decode(self, reads: Iterable[str]) -> bytes:
        raise NotImplementedError()


class Outputter(ABC):
    @abstractmethod
    def write(self, message: bytes) -> None:
        raise NotImplementedError()


class Aligner(ABC):
    """Adapter for alignment/consensus components which take raw reads and produce aligned reads or consensus strings."""

    @abstractmethod
    def align(self, reads: Iterable[str]) -> Iterable[str]:
        """Returns an iterable of aligned/consensus DNA strings from noisy reads."""

