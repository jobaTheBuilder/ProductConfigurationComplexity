from __future__ import annotations

import argparse
import shutil
from pathlib import Path


class Tooling:
    def rename_files(self, directory: Path, remove_original_file=True) -> str:
        directory = Path(directory)
        ttl_files = sorted(
            path for path in directory.iterdir() if path.is_file() and path.suffix == ".ttl"
        )
        index_width = max(3, len(str(len(ttl_files))))

        temporary_paths: list[tuple[Path, Path]] = []
        final_paths: list[tuple[Path, Path]] = []

        # Rename through temporary filenames first to avoid collisions with final names.
        for index, original_path in enumerate(ttl_files, start=1):
            temporary_path = directory / f"__tmp_kb_rename_{index}__.ttl"
            original_path.rename(temporary_path)
            temporary_paths.append((original_path, temporary_path))

        for index, (original_path, temporary_path) in enumerate(temporary_paths, start=1):
            final_path = directory / f"EKG{index:0{index_width}d}{temporary_path.suffix}"
            if remove_original_file:
                temporary_path.rename(final_path)
            else:
                # copy the file to the new location so that the original file is not deleted.
                shutil.copy2(temporary_path, final_path)
                temporary_path.rename(original_path)

            final_paths.append((original_path, final_path))

        mapping_path = directory / "EKG_filename_mapping.md"
        original_header = "Original filename"
        new_header = "New filename"
        rows = [
            (f"`{original_path.name}`", f"`{final_path.name}`")
            for original_path, final_path in final_paths
        ]
        original_width = max([len(original_header), *(len(original) for original, _ in rows)])
        new_width = max([len(new_header), *(len(new) for _, new in rows)])
        mapping_lines = [
            "# Filename Mapping",
            "",
            f"Normalized `{len(final_paths)}` `.ttl` files in `{directory}`.",
            "",
            f"| {original_header.ljust(original_width)} | {new_header.ljust(new_width)} |",
            f"| {'-' * original_width} | {'-' * new_width} |",
        ]
        mapping_lines.extend(
            f"| {original.ljust(original_width)} | {new.ljust(new_width)} |"
            for original, new in rows
        )
        mapping_path.write_text("\n".join(mapping_lines) + "\n", encoding="utf-8")

        return str(mapping_path)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", type=Path)
    args = parser.parse_args()

    tooling = Tooling()
    print(tooling.rename_files(args.directory, remove_original_file=False))


if __name__ == "__main__":
    main()
