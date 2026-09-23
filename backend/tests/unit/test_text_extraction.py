import pytest

from app.domain.exceptions import UnsupportedFileTypeError
from app.services.text_extraction import DocumentTextExtractor, PlainTextExtractor, TextExtractor


def test_plain_text_extractor_decodes_utf8():
    extractor = PlainTextExtractor()
    assert extractor.extract("Olá, mundo!".encode()) == "Olá, mundo!"


def test_plain_text_extractor_ignores_undecodable_bytes():
    extractor = PlainTextExtractor()
    assert extractor.extract(b"valid \xff\xfe bytes") == "valid  bytes"


def test_plain_text_extractor_only_supports_txt():
    extractor = PlainTextExtractor()
    assert extractor.supports("report.txt") is True
    assert extractor.supports("REPORT.TXT") is True
    assert extractor.supports("report.pdf") is False


def test_document_text_extractor_strips_nul_bytes():
    class NulByteExtractor(TextExtractor):
        def supports(self, filename: str) -> bool:
            return True

        def extract(self, content: bytes) -> str:
            return "before\x00after"

    extractor = DocumentTextExtractor(extractors=[NulByteExtractor()])
    assert extractor.extract("anything.txt", b"") == "beforeafter"


def test_document_text_extractor_dispatches_to_first_supporting_strategy():
    class RecordingExtractor(TextExtractor):
        def __init__(self, name: str, supported_ext: str):
            self.name = name
            self._ext = supported_ext
            self.called = False

        def supports(self, filename: str) -> bool:
            return filename.endswith(self._ext)

        def extract(self, content: bytes) -> str:
            self.called = True
            return self.name

    txt_extractor = RecordingExtractor("txt-result", ".txt")
    pdf_extractor = RecordingExtractor("pdf-result", ".pdf")
    extractor = DocumentTextExtractor(extractors=[txt_extractor, pdf_extractor])

    result = extractor.extract("doc.pdf", b"")

    assert result == "pdf-result"
    assert pdf_extractor.called is True
    assert txt_extractor.called is False


def test_document_text_extractor_raises_for_unsupported_extension():
    extractor = DocumentTextExtractor(extractors=[PlainTextExtractor()])
    with pytest.raises(UnsupportedFileTypeError):
        extractor.extract("spreadsheet.xlsx", b"")
