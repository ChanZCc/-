import re
import time
from rapidfuzz import process, fuzz

dirty_text = "你好 100*65"

choices = ["卡压大小头 102*76", "卡压大小头 100*80", "卡压大小头 100*25", "卡压大小头 100*32"]

alias_groups = {
	"卡压大小头": ["你好", "大小头", "异径头"],
}

spec_alias_groups = {
	"102": ["100"],
	"76": ["65"],
}


def build_alias_map(groups: dict[str, list[str]]) -> dict[str, str]:
	"""构建别名映射，将每个别名映射到其标准名称"""
	alias_map = {}
	for standard_name, aliases in groups.items():
		alias_map[standard_name] = standard_name
		for alias in aliases:
			alias_map[alias] = standard_name
	return alias_map


synonym_map = build_alias_map(alias_groups)
spec_alias_map = build_alias_map(spec_alias_groups)


def extract_name_and_spec(text: str) -> tuple[str, str]:
	"""提取名称和规格，规格格式例如 100*65 或 100x65"""
	cleaned = text.strip()
	match = re.search(r"(\d+\s*[xX*＊]\s*\d+)", cleaned)
	if not match:
		return cleaned, ""

	name = cleaned[:match.start()].strip()
	spec = match.group(1)
	return name, spec


def normalize_name(text: str) -> str:
	"""将名称字段精确映射为标准名称，避免局部字符串误替换"""
	cleaned = text.strip()
	return synonym_map.get(cleaned, cleaned)


def normalize_spec(spec: str) -> str:
	"""将规格中的别名值替换为标准值，并统一分隔符"""
	if not spec:
		return ""

	parts = re.split(r"\s*[xX*＊]\s*", spec.strip())
	normalized_parts = [spec_alias_map.get(part, part) for part in parts]
	return "*".join(normalized_parts)


def structured_scorer(query: str, choice: str, *, score_cutoff: float = 0) -> float:
	"""名称和规格分别比对，再计算综合得分"""
	query_name, query_spec = extract_name_and_spec(query)
	choice_name, choice_spec = extract_name_and_spec(choice)

	normalized_query_name = normalize_name(query_name)
	normalized_choice_name = normalize_name(choice_name)
	normalized_query_spec = normalize_spec(query_spec)
	normalized_choice_spec = normalize_spec(choice_spec)

	name_score = fuzz.ratio(normalized_query_name, normalized_choice_name)
	if normalized_query_spec and normalized_choice_spec:
		spec_score = fuzz.ratio(normalized_query_spec, normalized_choice_spec)
	elif not normalized_query_spec and not normalized_choice_spec:
		spec_score = 100
	else:
		spec_score = 0

	final_score = name_score * 0.4 + spec_score * 0.6
	return final_score if final_score >= score_cutoff else 0


def explain_match(query: str, choice: str) -> tuple[str, str, str, str, float, float, float]:
	"""返回匹配过程中的关键中间值，便于调试和展示"""
	query_name, query_spec = extract_name_and_spec(query)
	choice_name, choice_spec = extract_name_and_spec(choice)

	normalized_query_name = normalize_name(query_name)
	normalized_choice_name = normalize_name(choice_name)
	normalized_query_spec = normalize_spec(query_spec)
	normalized_choice_spec = normalize_spec(choice_spec)

	name_score = fuzz.ratio(normalized_query_name, normalized_choice_name)
	spec_score = fuzz.ratio(normalized_query_spec, normalized_choice_spec)
	final_score = name_score * 0.4 + spec_score * 0.6
	return (
		normalized_query_name,
		normalized_choice_name,
		normalized_query_spec,
		normalized_choice_spec,
		name_score,
		spec_score,
		final_score,
	)

# 计算相似度
start_time = time.time()
matches = process.extractOne(
	dirty_text,
	choices,
	scorer=structured_scorer,
)
end_time = time.time()

best_match = matches[0]
normalized_query_name, normalized_choice_name, normalized_query_spec, normalized_choice_spec, name_score, spec_score, final_score = explain_match(dirty_text, best_match)

print(f"耗时 {end_time - start_time:.4f} 秒")
print(f"最佳匹配: {best_match}, 综合相似度: {matches[1]}%")
print(f"名称归一化: {normalized_query_name} <-> {normalized_choice_name}, 名称得分: {name_score}%")
print(f"规格归一化: {normalized_query_spec} <-> {normalized_choice_spec}, 规格得分: {spec_score}%")
print(f"最终得分: {final_score}%")
