#!/usr/bin/env python3
"""
Wiki 기계 검증 스크립트

검증 항목:
1. Frontmatter 검증 (필수 필드 확인)
2. 스키마 검증 (타입, 상태, 필드 유효성)
3. 파일명 규칙 검증 (명명 규칙)
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Tuple

class WikiValidator:
    """Wiki 파일 검증"""

    # 타입별 필수 필드
    REQUIRED_FIELDS = {
        'decision': ['타입', '출처', '상태', '결정일', 'owner'],
        'pending': ['타입', '출처', '상태', '보류일', '다음_논의'],
        'action_item': ['타입', '출처', '상태', '담당자', '마감'],
        'rejected': ['타입', '출처', '상태'],
    }

    # 타입별 유효한 상태값
    VALID_STATES = {
        'decision': ['active', 'resolved', 'obsolete'],
        'pending': ['active', 'stale'],
        'action_item': ['pending', 'in_progress', 'completed', 'blocked'],
        'rejected': ['rejected'],
    }

    # 파일명 규칙 (정규식)
    FILENAME_PATTERNS = {
        'decision': r'^[가-힣a-z0-9\-]+-\d{4}-\d{2}-\d{2}-[가-힣a-z0-9\-]+\.md$',
        'pending': r'^[가-힣a-z0-9\-]+-\d{4}-\d{2}-\d{2}-[가-힣a-z0-9\-]+\.md$',
        'action_item': r'^action-\d{4}-\d{2}-\d{2}-[가-힣a-z0-9\-]+-[가-힣a-z0-9\-]+\.md$',
        'rejected': r'^rejected-\d{4}-\d{2}-\d{2}-[가-힣a-z0-9\-]+\.md$',
    }

    def __init__(self, wiki_root: str):
        self.wiki_root = Path(wiki_root)
        self.errors = []
        self.warnings = []

    def validate_all(self) -> Dict:
        """전체 Wiki 검증"""
        results = {
            'total_files': 0,
            'valid_files': 0,
            'errors': [],
            'warnings': [],
        }

        # 각 카테고리별 검증
        categories = ['decisions', 'pending', 'action_items', 'rejected']
        for category in categories:
            category_path = self.wiki_root / category
            if not category_path.exists():
                continue

            for md_file in category_path.glob('*.md'):
                results['total_files'] += 1
                file_type = self._map_category_to_type(category)

                file_errors, file_warnings = self.validate_file(md_file, file_type)

                if not file_errors:
                    results['valid_files'] += 1
                else:
                    results['errors'].extend(file_errors)

                results['warnings'].extend(file_warnings)

        return results

    def validate_file(self, filepath: Path, expected_type: str) -> Tuple[List[str], List[str]]:
        """개별 파일 검증"""
        errors = []
        warnings = []

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            # Frontmatter 추출
            if not content.startswith('---'):
                errors.append(f"{filepath.name}: Frontmatter이 없습니다")
                return errors, warnings

            frontmatter_end = content.find('---', 3)
            if frontmatter_end == -1:
                errors.append(f"{filepath.name}: Frontmatter 종료 마크(---)가 없습니다")
                return errors, warnings

            frontmatter_str = content[3:frontmatter_end].strip()

            try:
                frontmatter = self._parse_yaml(frontmatter_str)
            except Exception as e:
                errors.append(f"{filepath.name}: Frontmatter 파싱 실패 - {str(e)}")
                return errors, warnings

            # 1. Frontmatter 검증 (필수 필드)
            file_type = frontmatter.get('타입')
            if not file_type:
                errors.append(f"{filepath.name}: '타입' 필드가 없습니다")
                return errors, warnings

            required = self.REQUIRED_FIELDS.get(file_type, [])
            for field in required:
                if field not in frontmatter or frontmatter[field] is None:
                    errors.append(f"{filepath.name}: 필수 필드 '{field}'가 없습니다")

            # 2. 스키마 검증 (타입, 상태)
            if file_type not in ['decision', 'pending', 'action_item', 'rejected']:
                errors.append(f"{filepath.name}: 유효하지 않은 타입 '{file_type}'")
            else:
                # 상태 검증
                status = frontmatter.get('상태')
                valid_statuses = self.VALID_STATES.get(file_type, [])
                if status and status not in valid_statuses:
                    errors.append(f"{filepath.name}: 유효하지 않은 상태 '{status}' (타입: {file_type})")

            # 3. 파일명 규칙 검증
            pattern = self.FILENAME_PATTERNS.get(file_type)
            if pattern and not re.match(pattern, filepath.name):
                warnings.append(f"{filepath.name}: 파일명 규칙을 따르지 않습니다. 예: [영역]-YYYY-MM-DD-[설명].md")

            # 추가 검증: Decision revision
            if file_type == 'decision':
                if '이전_결정' in frontmatter and '변경_사유' not in frontmatter:
                    warnings.append(f"{filepath.name}: Decision revision이 있으면 '변경_사유' 필드를 명시해야 합니다")

            # 추가 검증: Pending의 다음_논의
            if file_type == 'pending':
                next_discuss = frontmatter.get('다음_논의')
                if next_discuss and next_discuss not in ['TBD', 'tbd']:
                    # 날짜 형식 검증 (YYYY-MM-DD)
                    if not re.match(r'^\d{4}-\d{2}-\d{2}$', str(next_discuss)):
                        warnings.append(f"{filepath.name}: '다음_논의'가 YYYY-MM-DD 형식이 아닙니다: {next_discuss}")

            # 추가 검증: Action item의 담당자
            if file_type == 'action_item':
                if not frontmatter.get('담당자'):
                    errors.append(f"{filepath.name}: Action item은 담당자가 필수입니다")

        except Exception as e:
            errors.append(f"{filepath.name}: 예상치 못한 오류 - {str(e)}")

        return errors, warnings

    def _map_category_to_type(self, category: str) -> str:
        """카테고리명을 타입으로 변환"""
        mapping = {
            'decisions': 'decision',
            'pending': 'pending',
            'action_items': 'action_item',
            'rejected': 'rejected',
        }
        return mapping.get(category, '')

    def _parse_yaml(self, content: str) -> Dict:
        """간단한 YAML 파서 (key: value 형식만 지원)"""
        result = {}
        for line in content.split('\n'):
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()

                # 값 정제
                if value.startswith('[') and value.endswith(']'):
                    # 리스트 파싱
                    value = [v.strip() for v in value[1:-1].split(',')]
                elif value.lower() in ['true', 'false']:
                    value = value.lower() == 'true'

                result[key] = value if value else None

        return result

    def print_report(self, results: Dict):
        """검증 결과 출력"""
        print("\n" + "="*60)
        print("📋 Wiki 기계 검증 결과")
        print("="*60)

        print(f"\n📊 통계:")
        print(f"  총 파일 수: {results['total_files']}")
        print(f"  통과 파일: {results['valid_files']}")
        print(f"  오류: {len(results['errors'])}")
        print(f"  경고: {len(results['warnings'])}")

        if results['errors']:
            print(f"\n❌ 오류 ({len(results['errors'])}):")
            for error in results['errors']:
                print(f"  - {error}")

        if results['warnings']:
            print(f"\n⚠️  경고 ({len(results['warnings'])}):")
            for warning in results['warnings']:
                print(f"  - {warning}")

        if not results['errors'] and not results['warnings']:
            print("\n✅ 모든 파일이 검증을 통과했습니다!")

        print("\n" + "="*60)

if __name__ == '__main__':
    import sys

    wiki_root = sys.argv[1] if len(sys.argv) > 1 else './wiki'

    validator = WikiValidator(wiki_root)
    results = validator.validate_all()
    validator.print_report(results)

    # 오류가 있으면 exit code 1
    sys.exit(1 if results['errors'] else 0)
