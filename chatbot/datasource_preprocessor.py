import json
import polib
import re
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set logging level based on environment variable
logger.setLevel(os.getenv("SERVER_LOGGING_LEVEL", "INFO").upper())

def extract_tooltips(po_file_path: str) -> dict:
	"""
	Extract tooltips from a .po file.

	:param po_file_path: Path to the .po file.
	:return: Dictionary containing tooltips.
	"""
	po = polib.pofile(po_file_path)
	tooltips = {}

	for entry in po:
		if "tooltip" in entry.msgid.lower():
			msgid = entry.msgid.strip()
			# Remove ".tooltip" at the end
			msgid = re.sub(r"\.tooltip$", "", msgid)
			# Process words split by '.'
			words = msgid.split(".")
			if len(words) > 1 and words[1] in ["Training", "Dataset"]:
				words.pop(1)  # Remove second word if it's "Training" or "Dataset"
			msgid = ".".join(words)
			tooltips[msgid] = entry.msgstr.strip()

	return tooltips

def update_json_with_tooltips(json_file_path: str, tooltips: dict) -> str:
	"""
	Update a JSON file with extracted tooltips.

	:param json_file_path: Path to the JSON file.
	:param tooltips: Dictionary of extracted tooltips.
	:return: Path to the updated JSON file.
	"""
	with open(json_file_path, "r", encoding="utf-8") as file:
		data = json.load(file)

	# Remove "Anchor" keys from all sections
	def remove_anchor_keys(sections: list) -> None:
		for section in sections:
			section.pop("Anchor", None)
			section.pop("linkHeadline", None)
			if "Subsections" in section:
				for subsection in section["Subsections"]:
					subsection.pop("Anchor", None)
					subsection.pop("linkHeadline", None)

	for panel in data:
		if "Sections" in panel:
			remove_anchor_keys(panel["Sections"])

	# Process sections for "Pages" PanelHeadline
	def process_sections(sections: list, tooltips: dict) -> None:
		for section in sections:
			if "Subsections" in section:
				for subsection in section["Subsections"]:
					sub_headline = re.sub(r"[\s:]+", "", subsection.get("SubHeadline", "")).lower()
					matched_sub_tooltips = []
					to_remove = []

					for msgid, msgstr in tooltips.items():
						words = msgid.split(".")
						if len(words) > 1:
							second_word = words[1].strip().lower()
						else:
							continue

						if sub_headline in second_word:
							logger.debug(f"Match found: {msgid}")
							matched_sub_tooltips.append({"Button": msgid, "Tooltip-text": msgstr})
							to_remove.append(msgid)

					if matched_sub_tooltips:
						subsection["Tooltips"] = matched_sub_tooltips
						for msgid in to_remove:
							del tooltips[msgid]

	def process_headlines(sections: list, tooltips: dict) -> None:
		for section in sections:
			headline = re.sub(r"[\s:]+", "", section.get("Headline", "")).lower()
			matched_headline_tooltips = []
			to_remove = []

			for msgid, msgstr in tooltips.items():
				words = msgid.split(".")
				if words:
					first_word = words[0].strip().lower()
				else:
					continue

				if headline in first_word:
					logger.debug(f"Match found: {msgid}")
					matched_headline_tooltips.append({"Button": msgid, "Tooltip-text": msgstr})
					to_remove.append(msgid)

			if matched_headline_tooltips:
				section["Tooltips"] = matched_headline_tooltips
				for msgid in to_remove:
					del tooltips[msgid]

	for panel in data:
		if panel.get("PanelHeadline", "").strip() == "Pages":
			if "Sections" in panel:
				process_sections(panel["Sections"], tooltips)
				process_headlines(panel["Sections"], tooltips)

	# Save updated JSON
	updated_json_path = "./data/rag_processed_data.json"
	with open(updated_json_path, "w", encoding="utf-8") as file:
		json.dump(data, file, indent=4, ensure_ascii=False)

	logger.info(f"Updated JSON saved to: {updated_json_path}")
	return updated_json_path

# Paths to the files
current_dir = os.path.dirname(os.path.abspath(__file__))
po_file_path = os.path.join(current_dir, "data\en-US.po")
json_file_path = os.path.join(current_dir, "data\HelpPage.json")

# Extract tooltips and update JSON
tooltips = extract_tooltips(po_file_path)
updated_json_path = update_json_with_tooltips(json_file_path, tooltips)
