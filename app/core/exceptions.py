class ResumeMatcherError(Exception):
    """Base exception for application-specific failures."""


class BusinessLogicNotImplementedError(ResumeMatcherError):
    """Raised when a planned business capability is intentionally absent."""


class FileParsingError(ResumeMatcherError):
    """Base exception for document parsing failures."""


class EmptyFileError(FileParsingError):
    """Raised when the uploaded file has no content."""


class UnsupportedFileTypeError(FileParsingError):
    """Raised when a file type is not supported by the parser."""


class InvalidFileError(FileParsingError):
    """Raised when the file content does not match the expected format."""


class CorruptedPDFError(FileParsingError):
    """Raised when a PDF cannot be read by available PDF parsers."""


class TextExtractionError(FileParsingError):
    """Raised when a supported file contains no extractable text."""


class SimilarityCalculationError(ResumeMatcherError):
    """Raised when semantic similarity cannot be calculated."""


class ScoringCalculationError(ResumeMatcherError):
    """Raised when final resume matching score cannot be calculated."""


class MissingGeminiAPIKeyError(ResumeMatcherError):
    """Raised when Gemini API access is requested without an API key."""


class ExplanationGenerationError(ResumeMatcherError):
    """Raised when Gemini cannot generate a valid explanation."""
