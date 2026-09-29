from pathlib import Path

from src.conditions import *

class TestExtensionCondition:
    def test_extension_matching_extension(self):
        """Verify extension matching works in the regular case."""
        condition = ExtensionCondition(".txt")
        assert condition.matches(Path("example.txt"))

    def test_extension_non_matching_extension(self):
        """Verify extension matching fails with a mismatched extension."""
        condition = ExtensionCondition(".txt")
        assert not condition.matches(Path("example.pdf"))

    def test_extension_no_mame(self):
        """Verify extension matching fails with a mismatched extension and no name."""
        condition = ExtensionCondition(".txt")
        assert not condition.matches(Path(".pdf"))

    def test_extension_different_casing_extension(self):
        """Verify extension matching fails with a mismatched cased extension."""
        condition = ExtensionCondition(".txt")
        assert not condition.matches(Path("example.TXT"))

class TestNameContainsCondition:
    def test_name_contains_exact_match(self):
        """Verify name contains matching succeeds when the substring IS in the file name (matching case)."""
        condition = NameContainsCondition("notes")
        assert condition.matches(Path("notes.txt"))

    def test_name_contains_at_start(self):
        """Verify name contains matching succeeds when the substring is at the start of the file name (matching case)."""
        condition = NameContainsCondition("notes")
        assert condition.matches(Path("notes_1.txt"))

    def test_name_contains_at_end(self):
        """Verify name contains matching succeeds when the substring is at the end of the file name (matching case)."""
        condition = NameContainsCondition("notes")
        assert condition.matches(Path("my_notes.md"))

    def test_name_contains_in_middle(self):
        """Verify name contains matching succeeds when the substring is in the middle of the file name (matching case)."""
        condition = NameContainsCondition("notes")
        assert condition.matches(Path("math_notes_2.pdf"))

    def test_name_contains_is_case_insensitive_by_default(self):
        """Verify by default contains matching succeeds when the substring does not match file name casing."""
        condition = NameContainsCondition("NOTES")
        assert condition.matches(Path("math_notes_2.pdf"))

    def test_name_contains_respects_case_when_enabled(self):
        """Verify name contains matching succeeds when case matters, and the substring matches file name."""
        condition = NameContainsCondition("noTEs", True)
        assert condition.matches(Path("noTEs.txt"))

    def test_name_contains_fails_on_case_mismatch_when_enabled(self):
        """Verify name contains matching fails when case matters, and the substring does not match file case."""
        condition = NameContainsCondition("noTEs", True)
        assert not condition.matches(Path("notes.txt"))

    def test_name_contains_fails_if_substring_missing(self):
        """Verify name matching fails when the substring is absent."""
        condition = NameContainsCondition("notes")
        assert not condition.matches(Path("report.pdf"))

    def test_name_contains_empty_pattern(self):
        """Verify an empty pattern matches any file name."""
        condition = NameContainsCondition("")
        assert condition.matches(Path("notes.txt"))

    def test_name_contains_uses_file_name_only(self):
        """Verify matching uses only the file name and ignores parent directories."""
        condition = NameContainsCondition("notes")
        assert condition.matches(Path("documents/work/my_notes.txt"))

    def test_name_contains_does_not_match_parent_directory(self):
        """Verify parent directory names are not considered when matching."""
        condition = NameContainsCondition("notes")
        assert not condition.matches(Path("notes/report.pdf"))


class TestNameStartsWithCondition:
    def test_name_starts_with_exact_match(self):
        """Verify name starts with succeeds when the substring IS in the file name (matching case)."""
        condition = NameStartsWithCondition("notes")
        assert condition.matches(Path("notes"))
        
    def test_name_starts_with_passes_at_start(self):
        """Verify name starts with succeeds when the substring is at the end of the file name (matching case)."""
        condition = NameStartsWithCondition("notes")
        assert condition.matches(Path("notes123.md"))

    def test_name_starts_with_fails_at_end(self):
        """Verify name starts with succeeds when the substring is at the end of the file name (matching case)."""
        condition = NameStartsWithCondition("notes")
        assert not condition.matches(Path("my_notes.md"))

    def test_name_starts_with_in_middle(self):
        """Verify name starts with succeeds when the substring is in the middle of the file name (matching case)."""
        condition = NameStartsWithCondition("notes")
        assert not condition.matches(Path("math_notes_2.pdf"))

    def test_name_starts_with_is_case_insensitive_by_default(self):
        """Verify by default name starts with succeeds when the substring does not match file name casing."""
        condition = NameStartsWithCondition("NoTES")
        assert condition.matches(Path("nOtes_2.pdf"))

    def test_name_starts_with_respects_case_when_enabled(self):
        """Verify name starts with succeeds when case matters, and the substring matches file name."""
        condition = NameStartsWithCondition("noTEs", True)
        assert condition.matches(Path("noTEs.txt"))

    def test_name_starts_with_fails_on_case_mismatch_when_enabled(self):
        """Verify name starts with fails when case matters, and the substring does not match file case."""
        condition = NameStartsWithCondition("noTEs", True)
        assert not condition.matches(Path("notes.txt"))

    def test_name_starts_with_include_extension_by_default(self):
        """Verify by default name starts with succeeds when the substring does not match file name casing."""
        condition = NameStartsWithCondition("notes.txt")
        assert condition.matches(Path("notes.txt"))

    def test_name_starts_with_includes_extension_when_enabled(self):
        """Verify name starts with succeeds when extension is included and substring matches."""
        condition = NameStartsWithCondition("notes.t", include_extension=True)
        assert condition.matches(Path("notes.txt"))

    def test_name_starts_with_fails_on_extension_included_when_enabled(self):
        """Verify name starts with fails when extension is included and substring does not match."""
        condition = NameStartsWithCondition("notes.i", include_extension=True)
        assert not condition.matches(Path("notes.t"))

    def test_name_starts_with_does_not_includes_extension_when_disabled(self):
        """Verify name starts with fails when extension is unincluded and substring does match."""
        condition = NameStartsWithCondition("notes", include_extension=False)
        assert condition.matches(Path("notes.txt"))

    def test_name_starts_with_fails_on_extension_unincluded_when_enabled(self):
        """Verify name starts with fails when extension is unincluded and substring does not match."""
        condition = NameStartsWithCondition("notes.txt", include_extension=False)
        assert not condition.matches(Path("notes.txt"))

    def test_name_starts_with_fails_if_substring_missing(self):
        """Verify name starts with fails when the substring is absent."""
        condition = NameStartsWithCondition("notes")
        assert not condition.matches(Path("report.pdf"))

    def test_name_starts_with_multiple_suffixes_included(self):
        """Verify matching includes all suffixes when extension matching is enabled."""
        condition = NameStartsWithCondition("archive.tar", include_extension=True)
        assert condition.matches(Path("archive.tar.gz"))

    def test_name_starts_with_multiple_suffixes_final_extension_ignored(self):
        """Verify only the final extension is ignored when extension matching is disabled."""
        condition = NameStartsWithCondition("archive.tar", include_extension=False)
        assert condition.matches(Path("archive.tar.gz"))

    def test_name_starts_with_empty_pattern(self):
        """Verify an empty pattern matches the start of any file name."""
        condition = NameStartsWithCondition("")
        assert condition.matches(Path("notes.txt"))

    def test_name_starts_with_uses_file_name_only(self):
        condition = NameStartsWithCondition("notes")
        assert condition.matches(Path("documents/work/notes.txt"))


class TestNameEndsWithCondition:
    def test_name_ends_with_exact_match(self):
        """Verify an exact file name match succeeds."""
        condition = NameEndsWithCondition("notes")
        assert condition.matches(Path("notes"))

    def test_name_ends_with_passes_at_end(self):
        """Verify a match succeeds when the substring is at the end of the file name."""
        condition = NameEndsWithCondition("notes")
        assert condition.matches(Path("my_notes"))

    def test_name_ends_with_fails_at_start(self):
        """Verify a match fails when the substring appears only at the start of the file name."""
        condition = NameEndsWithCondition("notes")
        assert not condition.matches(Path("notes_123.md"))

    def test_name_ends_with_fails_in_middle(self):
        """Verify a match fails when the substring appears only in the middle of the file name."""
        condition = NameEndsWithCondition("notes")
        assert not condition.matches(Path("my_notes_2.pdf"))

    def test_name_ends_with_is_case_insensitive_by_default(self):
        """Verify matching is case-insensitive by default."""
        condition = NameEndsWithCondition("NoTES")
        assert condition.matches(Path("my_nOtes"))

    def test_name_ends_with_respects_case_when_enabled(self):
        """Verify matching succeeds when case sensitivity is enabled and casing matches."""
        condition = NameEndsWithCondition("noTEs", True)
        assert condition.matches(Path("my_noTEs"))

    def test_name_ends_with_fails_on_case_mismatch_when_enabled(self):
        """Verify matching fails when case sensitivity is enabled and casing differs."""
        condition = NameEndsWithCondition("noTEs", True)
        assert not condition.matches(Path("my_notes"))

    def test_name_ends_with_includes_extension_by_default(self):
        """Verify the file extension is included in matching by default."""
        condition = NameEndsWithCondition(".txt")
        assert condition.matches(Path("notes.txt"))

    def test_name_ends_with_includes_extension_when_enabled(self):
        """Verify matching can include characters from the extension when enabled."""
        condition = NameEndsWithCondition("es.txt", include_extension=True)
        assert condition.matches(Path("notes.txt"))

    def test_name_ends_with_fails_when_extension_does_not_match(self):
        """Verify matching fails when the included extension characters do not match."""
        condition = NameEndsWithCondition(".pdf", include_extension=True)
        assert not condition.matches(Path("notes.txt"))

    def test_name_ends_with_ignores_extension_when_disabled(self):
        """Verify the base file name can match when extension matching is disabled."""
        condition = NameEndsWithCondition("notes", include_extension=False)
        assert condition.matches(Path("my_notes.txt"))

    def test_name_ends_with_fails_on_extension_when_disabled(self):
        """Verify a pattern containing the extension fails when extension matching is disabled."""
        condition = NameEndsWithCondition("notes.txt", include_extension=False)
        assert not condition.matches(Path("notes.txt"))

    def test_name_ends_with_fails_if_substring_missing(self):
        """Verify matching fails when the substring is absent."""
        condition = NameEndsWithCondition("notes")
        assert not condition.matches(Path("report.pdf"))

    def test_name_ends_with_multiple_suffixes_included(self):
        """Verify matching can include multiple suffixes when extension matching is enabled."""
        condition = NameEndsWithCondition(".tar.gz", include_extension=True)
        assert condition.matches(Path("archive.tar.gz"))

    def test_name_ends_with_multiple_suffixes_final_extension_ignored(self):
        """Verify only the final extension is ignored when extension matching is disabled."""
        condition = NameEndsWithCondition(".tar", include_extension=False)
        assert condition.matches(Path("archive.tar.gz"))

    def test_name_ends_with_final_extension_fails_when_disabled(self):
        """Verify the final extension cannot be matched when extension matching is disabled."""
        condition = NameEndsWithCondition(".gz", include_extension=False)
        assert not condition.matches(Path("archive.tar.gz"))

    def test_name_ends_with_empty_pattern(self):
        """Verify an empty pattern matches the end of any file name."""
        condition = NameEndsWithCondition("")
        assert condition.matches(Path("notes.txt"))

    def test_name_ends_with_uses_file_name_only(self):
        condition = NameEndsWithCondition("notes", include_extension=False)
        assert condition.matches(Path("documents/work/my_notes.txt"))


class TestExactNameCondition:
    def test_exact_name_matches_exact_file_name(self):
        """Verify an exact file name match succeeds."""
        condition = ExactNameCondition("notes.txt")
        assert condition.matches(Path("notes.txt"))

    def test_exact_name_fails_when_prefix_differs(self):
        """Verify matching fails when extra characters appear before the expected name."""
        condition = ExactNameCondition("notes.txt")
        assert not condition.matches(Path("my_notes.txt"))

    def test_exact_name_fails_when_suffix_differs(self):
        """Verify matching fails when extra characters appear after the expected name."""
        condition = ExactNameCondition("notes.txt")
        assert not condition.matches(Path("notes.txt.backup"))

    def test_exact_name_fails_on_partial_match(self):
        """Verify matching fails when only part of the file name matches."""
        condition = ExactNameCondition("notes")
        assert not condition.matches(Path("notes123"))

    def test_exact_name_is_case_insensitive_by_default(self):
        """Verify matching is case-insensitive by default."""
        condition = ExactNameCondition("NoTES.txt")
        assert condition.matches(Path("nOtes.TXT"))

    def test_exact_name_respects_case_when_enabled(self):
        """Verify matching succeeds when case sensitivity is enabled and casing matches."""
        condition = ExactNameCondition("noTEs.txt", True)
        assert condition.matches(Path("noTEs.txt"))

    def test_exact_name_fails_on_case_mismatch_when_enabled(self):
        """Verify matching fails when case sensitivity is enabled and casing differs."""
        condition = ExactNameCondition("noTEs.txt", True)
        assert not condition.matches(Path("notes.txt"))

    def test_exact_name_includes_extension_by_default(self):
        """Verify the extension is included in exact matching by default."""
        condition = ExactNameCondition("notes.txt")
        assert condition.matches(Path("notes.txt"))

    def test_exact_name_includes_extension_when_enabled(self):
        """Verify exact matching includes the extension when enabled."""
        condition = ExactNameCondition("notes.txt", include_extension=True)
        assert condition.matches(Path("notes.txt"))

    def test_exact_name_fails_when_extension_differs(self):
        """Verify exact matching fails when the extension differs."""
        condition = ExactNameCondition("notes.pdf", include_extension=True)
        assert not condition.matches(Path("notes.txt"))

    def test_exact_name_ignores_extension_when_disabled(self):
        """Verify matching compares only the base file name when extension matching is disabled."""
        condition = ExactNameCondition("notes", include_extension=False)
        assert condition.matches(Path("notes.txt"))

    def test_exact_name_fails_when_extension_is_in_pattern_but_disabled(self):
        """Verify a pattern containing an extension fails when extension matching is disabled."""
        condition = ExactNameCondition("notes.txt", include_extension=False)
        assert not condition.matches(Path("notes.txt"))

    def test_exact_name_fails_if_name_differs(self):
        """Verify matching fails when the file name is different."""
        condition = ExactNameCondition("notes.txt")
        assert not condition.matches(Path("report.pdf"))

    def test_exact_name_matches_multiple_suffixes_when_included(self):
        """Verify the complete file name including multiple suffixes can match."""
        condition = ExactNameCondition("archive.tar.gz", include_extension=True)
        assert condition.matches(Path("archive.tar.gz"))

    def test_exact_name_matches_stem_with_multiple_suffixes_when_disabled(self):
        """Verify only the final extension is removed when extension matching is disabled."""
        condition = ExactNameCondition("archive.tar", include_extension=False)
        assert condition.matches(Path("archive.tar.gz"))

    def test_exact_name_fails_with_full_name_when_extension_disabled(self):
        """Verify the full file name does not match when the final extension is excluded."""
        condition = ExactNameCondition("archive.tar.gz", include_extension=False)
        assert not condition.matches(Path("archive.tar.gz"))

    def test_exact_name_empty_pattern_fails_on_nonempty_name(self):
        """Verify an empty pattern does not exactly match a non-empty file name."""
        condition = ExactNameCondition("")
        assert not condition.matches(Path("notes.txt"))

    def test_exact_name_uses_file_name_only(self):
        condition = ExactNameCondition("notes.txt")
        assert condition.matches(Path("documents/work/notes.txt"))


class TestAndCondition:
    def test_and_both_children_true(self):
        """Verify the and condition succeeds when it has 2 conditions, both True."""
        condition = AndCondition([ExtensionCondition(".txt"), NameContainsCondition("notes")])
        assert condition.matches(Path("notes.txt"))

    def test_and_first_child_false(self):
        """Verify the and condition fails when it has 2 conditions, the first of which fails."""
        condition = AndCondition([ExtensionCondition(".txt"), NameContainsCondition("notes")])
        assert not condition.matches(Path("notes.md"))

    def test_and_second_child_false(self):
        """Verify the and condition fails when it has 2 conditions, the second of which fails."""
        condition = AndCondition([ExtensionCondition(".txt"), NameContainsCondition("notes")])
        assert not condition.matches(Path("report.txt"))

    def test_and_both_children_false(self):
        """Verify the and condition fails when it has 2 conditions, both False."""
        condition = AndCondition([ExtensionCondition(".txt"), NameContainsCondition("notes")])
        assert not condition.matches(Path("report.pdf"))

    def test_and_one_condition_true(self):
        """Verify the and condition passes when it has 1 True condition."""
        condition = AndCondition([ExtensionCondition(".txt")])
        assert condition.matches(Path("report.txt"))

    def test_and_one_condition_false(self):
        """Verify the and condition fails when it has 1 False condition."""
        condition = AndCondition([ExtensionCondition(".txt")])
        assert not condition.matches(Path("report.pdf"))

    def test_and_no_conditions(self):
        """Verify the and condition fails when it has no conditions."""
        condition = AndCondition([])
        assert not condition.matches(Path("report.pdf"))

class TestOrCondition:
    def test_or_both_children_true(self):
        """Verify the or condition succeeds when it has 2 conditions, both True."""
        condition = OrCondition([ExtensionCondition(".txt"), NameContainsCondition("notes")])
        assert condition.matches(Path("notes.txt"))

    def test_or_first_child_false(self):
        """Verify the or condition succeeds when it has 2 conditions, the first of which fails."""
        condition = OrCondition([ExtensionCondition(".txt"), NameContainsCondition("notes")])
        assert condition.matches(Path("notes.md"))

    def test_or_second_child_false(self):
        """Verify the or condition succeeds when it has 2 conditions, the second of which fails."""
        condition = OrCondition([ExtensionCondition(".txt"), NameContainsCondition("notes")])
        assert condition.matches(Path("report.txt"))

    def test_or_both_children_false(self):
        """Verify the or condition fails when it has 2 conditions, both False."""
        condition = OrCondition([ExtensionCondition(".txt"), NameContainsCondition("notes")])
        assert not condition.matches(Path("report.pdf"))

    def test_or_one_condition_true(self):
        """Verify the or condition passes when it has 1 True condition."""
        condition = OrCondition([ExtensionCondition(".txt")])
        assert condition.matches(Path("report.txt"))

    def test_or_one_condition_false(self):
        """Verify the or condition fails when it has 1 False condition."""
        condition = OrCondition([ExtensionCondition(".txt")])
        assert not condition.matches(Path("report.pdf"))

    def test_or_no_conditions(self):
        """Verify the or condition fails when it has no conditions."""
        condition = OrCondition([])
        assert not condition.matches(Path("report.pdf"))

class TestSizeCondition:
    def test_size_greater_than_inclusive(self, tmp_path):
        """Verify the size condition succeeds and fails appropriately for comparing a file greater than or equal to the size."""
        file = tmp_path / "notes.txt"
        file.write_bytes(b"x" * 9)
        condition = SizeCondition(10, comparison="gte")
        assert not condition.matches(file)
        file.write_bytes(b"x" * 10)
        assert condition.matches(file)
        file.write_bytes(b"x" * 11)
        assert condition.matches(file)

    def test_size_greater_than_exclusive(self, tmp_path):
        """Verify the size condition succeeds and fails appropriately for comparing a file greater than the size."""
        file = tmp_path / "notes.txt"
        file.write_bytes(b"x" * 9)
        condition = SizeCondition(10, comparison="gt")
        assert not condition.matches(file)
        file.write_bytes(b"x" * 10)
        assert not condition.matches(file)
        file.write_bytes(b"x" * 11)
        assert condition.matches(file)

    def test_size_less_than_inclusive(self, tmp_path):
        """Verify the size condition succeeds and fails appropriately for comparing a file less than or equal to the size."""
        file = tmp_path / "notes.txt"
        file.write_bytes(b"x" * 9)
        condition = SizeCondition(10, comparison="lte")
        assert condition.matches(file)
        file.write_bytes(b"x" * 10)
        assert condition.matches(file)
        file.write_bytes(b"x" * 11)
        assert not condition.matches(file)

    def test_size_less_than_exclusive(self, tmp_path):
        """Verify the size condition succeeds and fails appropriately for comparing a file less than the size."""
        file = tmp_path / "notes.txt"
        file.write_bytes(b"x" * 9)
        condition = SizeCondition(10, comparison="lt")
        assert condition.matches(file)
        file.write_bytes(b"x" * 10)
        assert not condition.matches(file)
        file.write_bytes(b"x" * 11)
        assert not condition.matches(file)

    def test_size_equal(self, tmp_path):
        """Verify the size condition succeeds and fails appropriately for comparing a file equal the size."""
        file = tmp_path / "notes.txt"
        file.write_bytes(b"x" * 9)
        condition = SizeCondition(10, comparison="eq")
        assert not condition.matches(file)
        file.write_bytes(b"x" * 10)
        assert condition.matches(file)
        file.write_bytes(b"x" * 11)
        assert not condition.matches(file)




