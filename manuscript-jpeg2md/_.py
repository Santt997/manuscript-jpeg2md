#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path
import json
import sys

from PIL import Image

from surya.foundation import FoundationPredictor
from surya.recognition import RecognitionPredictor
from surya.detection import DetectionPredictor


def load_imgs(folder: Path) -> list[Path]:
    exts : tuple[str, ...] = ('*.jpg', '*.jpeg', '*.JPG', '*.JPEG')
    imgs : list[Path] = []
    for e in exts:
        imgs.extend(folder.glob(e))
    return sorted(imgs)


def build_notebook(lines: list[str]) -> dict:
    """Build a minimal nbformat-4 notebook with one markdown cell."""
    return {
        'nbformat': 4,
        'nbformat_minor': 5,
        'metadata': {},
        'cells': [
            {
                'cell_type': 'markdown',
                'metadata': {},
                'source': [l + '\n' for l in lines[:-1]] + lines[-1:],
            }
        ] if lines else [],
    }


def main() -> None:

    if len(sys.argv) < 2:
        print('Use: python ocr.py <directory>')
        sys.exit(1)

    target_dir : Path = Path(sys.argv[1]).resolve()

    if not target_dir.is_dir():
        print(f'Directory inexistent: {target_dir}')
        sys.exit(1)

    imgs : list[Path] = load_imgs(target_dir)

    if not imgs:
        print('No hay .JPEGs')
        return

    print(f'Directory : {target_dir}')
    print(f'Imgs   : {len(imgs)}')

    print('Loading models Surya...')

    # ✅ LOAD 1 ONLY TIME (CRITIC)
    foundation = FoundationPredictor()
    detector = DetectionPredictor()
    recognizer = RecognitionPredictor(foundation)

    for i, img_path in enumerate(imgs, start=1):

        print(f'[{i}/{len(imgs)}] {img_path.name}')

        try:
            image = Image.open(img_path).convert('RGB')

            # 🔥 RECONOCIMIENT & DETECTION INTEGRATED (SURYA 0.17.1)
            preds = recognizer([image], det_predictor=detector)

            lines : list[str] = []
            for page in preds:
                for line in page.text_lines:
                    txt : str = line.text.strip()
                    if txt:
                        lines.append(txt)

            out_file = img_path.with_suffix('.ipynb')
            out_file.write_text(
                json.dumps(build_notebook(lines), ensure_ascii=False, indent=1),
                encoding='utf-8',
            )

            print(f'    -> {out_file.name}')

        except Exception as e:
            print(f'    ERROR: {repr(e)}')


if __name__ == '__main__':
    main()