"""
Core data model, scanner, and file manager for Snippets and Collections.
Supports:
- Hierarchical folder collections (nested directories).
- Snippet bundles (folder with .algo, .md, pictures, companion files).
- Standalone snippet files with siblings (.algo, .md, .png, .txt, etc.).
- Joining / attaching Markdown files, Pictures, or any actual files.
"""

import os
import shutil
import re
from typing import List, Dict, Optional, Tuple, Any

# Known metadata fallback for legacy root examples
KNOWN_EXAMPLES_META = {
    "somme_diviseurs.algo": {
        "title": "Somme des Diviseurs",
        "category": "Boucle Pour & Procédure",
        "desc": "Calcul de la somme des diviseurs d'un entier avec boucle Pour et procédure avec passage par variable (@n)."
    },
    "palindrome.algo": {
        "title": "Vérification de Palindrome",
        "category": "Chaînes & Boucle Répéter",
        "desc": "Algorithme vérifiant si un mot est un palindrome avec boucle Répéter...Jusqu'à."
    },
    "gestion_eleves.algo": {
        "title": "Mention des Élèves",
        "category": "Enregistrement & Selon",
        "desc": "Structure de données Enregistrement (Record) et aiguillage conditionnel Selon (match/case) avec intervalles."
    },
    "tri_bulles.algo": {
        "title": "Tri à Bulles",
        "category": "Tableau & Algorithme de Tri",
        "desc": "Tri classique d'un tableau d'entiers avec permutation et boucle Tant que / Pour."
    },
    "matrice_alea.algo": {
        "title": "Matrice Aléatoire",
        "category": "Tableau 2D & Aléa",
        "desc": "Remplissage et affichage d'une matrice à 2 dimensions avec la fonction Aléa."
    },
    "players_ranking.algo": {
        "title": "Classement des Joueurs",
        "category": "Tableau d'Enregistrements",
        "desc": "Gestion complète d'un tournoi avec tableau d'enregistrements (Player), saisie, rounds et classement."
    }
}

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".svg", ".bmp", ".webp", ".gif", ".ico"}
CODE_EXTENSIONS = {".algo", ".py"}
MD_EXTENSIONS = {".md", ".markdown"}


class SnippetItem:
    """Represents a code snippet and its associated attachments."""

    def __init__(
        self,
        key: str,
        title: str,
        category: str,
        code_file: str,
        code: str,
        folder_path: str,
        is_bundle: bool = False,
        desc: str = "",
        md_file: Optional[str] = None,
        image_files: Optional[List[str]] = None,
        companion_files: Optional[List[str]] = None,
    ):
        self.key = key
        self.title = title
        self.category = category
        self.code_file = code_file
        self.code = code
        self.folder_path = folder_path
        self.is_bundle = is_bundle
        self.desc = desc
        self.md_file = md_file
        self.companion_files = companion_files or []
        # Keep image_files synced for any legacy caller
        self.image_files = image_files if image_files is not None else [
            f for f in self.companion_files if os.path.splitext(f)[1].lower() in IMAGE_EXTENSIONS
        ]
        self.lines_count = len(code.splitlines()) if code else 0

    @property
    def filename(self) -> str:
        return os.path.basename(self.code_file) if self.code_file else ""

    def get_md_content(self) -> str:
        if not self.md_file or not os.path.exists(self.md_file):
            return ""
        try:
            with open(self.md_file, "r", encoding="utf-8") as f:
                return f.read()
        except UnicodeDecodeError:
            try:
                with open(self.md_file, "r", encoding="latin-1") as f:
                    return f.read()
            except Exception:
                return ""
        except Exception:
            return ""

    def get_first_lines_md(self, max_lines: int = 4) -> str:
        """Extracts up to max_lines lines from the Markdown file to describe the snippet."""
        md_text = self.get_md_content().strip()
        if not md_text:
            return ""
        lines = [l.strip() for l in md_text.splitlines() if l.strip()]
        cleaned = []
        for l in lines[:max_lines]:
            c = re.sub(r"^#+\s*", "", l)
            c = re.sub(r"[*_`]", "", c).strip()
            if c:
                cleaned.append(c)
        return "\n".join(cleaned)

    def reload(self):
        """Reloads code and attached files from disk."""
        if self.code_file and os.path.exists(self.code_file):
            try:
                with open(self.code_file, "r", encoding="utf-8") as f:
                    self.code = f.read()
            except UnicodeDecodeError:
                with open(self.code_file, "r", encoding="latin-1") as f:
                    self.code = f.read()
            self.lines_count = len(self.code.splitlines())

        # Refresh files in folder
        if self.is_bundle and os.path.isdir(self.folder_path):
            self.image_files = []
            self.companion_files = []
            self.md_file = None
            for item in sorted(os.listdir(self.folder_path)):
                p = os.path.join(self.folder_path, item)
                if not os.path.isfile(p):
                    continue
                ext = os.path.splitext(item)[1].lower()
                if ext in CODE_EXTENSIONS:
                    continue
                elif ext in MD_EXTENSIONS:
                    if not self.md_file or item.lower().startswith("readme") or item == os.path.splitext(self.filename)[0] + ".md":
                        self.md_file = p
                    else:
                        self.companion_files.append(p)
                elif ext in IMAGE_EXTENSIONS:
                    self.image_files.append(p)
                    self.companion_files.append(p)
                else:
                    self.companion_files.append(p)


class CollectionNode:
    """Represents a category/collection folder in the snippets hierarchy."""

    def __init__(self, name: str, folder_path: str, rel_path: str = ""):
        self.name = name
        self.folder_path = folder_path
        self.rel_path = rel_path
        self.subcollections: List['CollectionNode'] = []
        self.snippets: List[SnippetItem] = []

    def get_all_snippets(self) -> List[SnippetItem]:
        all_s = list(self.snippets)
        for sc in self.subcollections:
            all_s.extend(sc.get_all_snippets())
        return all_s


def _clean_title(raw_name: str) -> str:
    """Cleans directory or file names into readable titles."""
    base = os.path.splitext(raw_name)[0]
    base = re.sub(r"^\d+[-_]", "", base)  # Remove numeric prefixes e.g. 01_
    return base.replace("_", " ").strip().title()


def _read_file_safe(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except UnicodeDecodeError:
        try:
            with open(path, "r", encoding="latin-1") as f:
                return f.read()
        except Exception:
            return ""
    except Exception:
        return ""


def get_default_snippets_dirs() -> List[str]:
    """Returns the ordered list of snippet directories to scan."""
    from ui.platform_utils import get_bundle_dir

    dirs = []
    base_root = get_bundle_dir()
    
    # 1. Primary snippets directory
    p_snippets = os.path.join(base_root, "snippets")
    if os.path.exists(p_snippets):
        dirs.append(p_snippets)

    # 2. Examples directory
    p_examples = os.path.join(base_root, "examples")
    if os.path.exists(p_examples):
        dirs.append(p_examples)

    # 3. User local snippets directory (~/.config/algoo/snippets)
    user_snippets = os.path.expanduser("~/.config/algoo/snippets")
    if os.path.exists(user_snippets):
        dirs.append(user_snippets)

    return dirs


def extract_md_metadata(md_path: Optional[str], default_title: str) -> Tuple[str, str]:
    """
    Extracts title and a 4-line description dynamically from the Markdown file.
    No hardcoding: reads directly from the markdown content.
    """
    if not md_path or not os.path.isfile(md_path):
        return default_title, f"Extrait {default_title}"

    text = _read_file_safe(md_path).strip()
    if not text:
        return default_title, f"Extrait {default_title}"

    lines = [l.strip() for l in text.splitlines() if l.strip()]
    title = default_title
    if lines and lines[0].startswith("#"):
        t = re.sub(r"^#+\s*", "", lines[0]).strip()
        if t:
            title = t

    desc_lines = []
    for l in lines[:4]:
        c = re.sub(r"^#+\s*", "", l)
        c = re.sub(r"[*_`]", "", c).strip()
        if c:
            desc_lines.append(c)

    desc = "\n".join(desc_lines) if desc_lines else f"Extrait {title}"
    return title, desc


def _inspect_folder_as_bundle(folder_path: str, category_name: str) -> Optional[SnippetItem]:
    """
    Checks if a folder is a leaf snippet bundle.
    A leaf snippet folder contains at least one .algo file, and has no subdirectories with .algo files.
    All files except the primary .algo and primary .md are listed in companion_files.
    """
    if not os.path.isdir(folder_path):
        return None

    algo_files = []
    md_files = []
    companion_files = []
    has_subdirs = False

    for entry in sorted(os.listdir(folder_path)):
        full_p = os.path.join(folder_path, entry)
        if os.path.isdir(full_p):
            if not entry.startswith(".") and entry != "__pycache__":
                has_subdirs = True
            continue
        if not os.path.isfile(full_p):
            continue
        ext = os.path.splitext(entry)[1].lower()
        if ext == ".algo":
            algo_files.append(full_p)
        elif ext in MD_EXTENSIONS:
            md_files.append(full_p)
        else:
            companion_files.append(full_p)

    # If it has subdirectories or no .algo files, or multiple .algo files, it's not a single snippet bundle
    if has_subdirs or len(algo_files) != 1:
        return None

    # Primary algo file
    primary_algo = algo_files[0]
    folder_name = os.path.basename(folder_path)
    algo_base = os.path.splitext(os.path.basename(primary_algo))[0]

    c_folder = _clean_title(folder_name).lower().replace(" ", "")
    c_algo = _clean_title(algo_base).lower().replace(" ", "")

    is_matching_bundle = (c_folder == c_algo) or (c_folder in c_algo) or (c_algo in c_folder)
    has_algo_named_companion = any(
        os.path.splitext(os.path.basename(f))[0].lower().startswith(algo_base.lower())
        for f in (md_files + companion_files)
    )

    if not is_matching_bundle and not has_algo_named_companion:
        return None
    folder_name = os.path.basename(folder_path)
    default_title = _clean_title(folder_name)

    # Pick best markdown file
    chosen_md = None
    if md_files:
        base_target = os.path.splitext(os.path.basename(primary_algo))[0].lower()
        for mf in md_files:
            m_base = os.path.splitext(os.path.basename(mf))[0].lower()
            if m_base == base_target or m_base == "readme":
                chosen_md = mf
                break
        if not chosen_md:
            chosen_md = md_files[0]
        for mf in md_files:
            if mf != chosen_md:
                companion_files.append(mf)

    for af in algo_files[1:]:
        companion_files.append(af)

    companion_files = sorted(companion_files, key=lambda p: os.path.basename(p).lower())

    code = _read_file_safe(primary_algo)
    title, desc = extract_md_metadata(chosen_md, default_title)

    return SnippetItem(
        key=folder_path,
        title=title,
        category=category_name,
        code_file=primary_algo,
        code=code,
        folder_path=folder_path,
        is_bundle=True,
        desc=desc,
        md_file=chosen_md,
        companion_files=companion_files
    )


def scan_snippets_tree(root_dirs: Optional[List[str]] = None) -> List[CollectionNode]:
    """
    Scans directories and produces a tree of CollectionNode hierarchy.
    Handles nested folders, bundle folders, and standalone .algo files.
    """
    if root_dirs is None:
        root_dirs = get_default_snippets_dirs()

    top_collections: List[CollectionNode] = []
    seen_snippet_names = set()

    def scan_directory(dir_path: str, category_label: str) -> CollectionNode:
        node = CollectionNode(
            name=_clean_title(category_label),
            folder_path=dir_path,
            rel_path=os.path.basename(dir_path)
        )

        entries = sorted(os.listdir(dir_path))
        # 1. First check subdirectories
        for entry in entries:
            if entry.startswith(".") or entry == "__pycache__":
                continue
            entry_path = os.path.join(dir_path, entry)
            if os.path.isdir(entry_path):
                # Is it a bundle snippet?
                bundle_snippet = _inspect_folder_as_bundle(entry_path, node.name)
                if bundle_snippet and bundle_snippet.filename not in seen_snippet_names:
                    seen_snippet_names.add(bundle_snippet.filename)
                    node.snippets.append(bundle_snippet)
                elif not bundle_snippet:
                    # Recursive collection
                    sub_node = scan_directory(entry_path, entry)
                    if sub_node.snippets or sub_node.subcollections:
                        node.subcollections.append(sub_node)

        # 2. Check loose standalone files in this directory
        for entry in entries:
            if not entry.endswith(".algo"):
                continue
            algo_path = os.path.join(dir_path, entry)
            if entry in seen_snippet_names:
                continue
            seen_snippet_names.add(entry)

            base_name = os.path.splitext(entry)[0]
            default_title = _clean_title(base_name)

            # Check for sibling files with same base name
            md_file = None
            for ext in MD_EXTENSIONS:
                cand = os.path.join(dir_path, base_name + ext)
                if os.path.isfile(cand):
                    md_file = cand
                    break

            title, desc = extract_md_metadata(md_file, default_title)

            companion_files = []
            for item in entries:
                if item == entry or (md_file and item == os.path.basename(md_file)):
                    continue
                item_p = os.path.join(dir_path, item)
                if not os.path.isfile(item_p):
                    continue
                if item.startswith(base_name) or not item.endswith(".algo"):
                    companion_files.append(item_p)

            companion_files = sorted(companion_files, key=lambda p: os.path.basename(p).lower())

            snippet = SnippetItem(
                key=algo_path,
                title=title,
                category=node.name,
                code_file=algo_path,
                code=_read_file_safe(algo_path),
                folder_path=dir_path,
                is_bundle=False,
                desc=desc,
                md_file=md_file,
                companion_files=companion_files
            )
            node.snippets.append(snippet)

        return node

    for r_dir in root_dirs:
        if not os.path.isdir(r_dir):
            continue
        col_node = scan_directory(r_dir, os.path.basename(r_dir))
        # If the root folder has only subcollections and no top-level snippets, we can surface subcollections
        if col_node.snippets:
            top_collections.append(col_node)
        elif col_node.subcollections:
            for sc in col_node.subcollections:
                top_collections.append(sc)

    return top_collections


def get_all_snippets_flat(collections: Optional[List[CollectionNode]] = None) -> List[SnippetItem]:
    """Flattens all snippets from collections tree."""
    if collections is None:
        collections = scan_snippets_tree()
    res = []
    for c in collections:
        res.extend(c.get_all_snippets())
    return res


def join_file_to_snippet(snippet: SnippetItem, source_file_path: str) -> str:
    """
    Joins/attaches an external file (Markdown, Picture, or actual data file) to a snippet.
    - If snippet is a bundle folder, copies into the folder.
    - If standalone file, upgrades it to a bundle folder and moves/copies files.
    Returns destination path.
    """
    if not os.path.exists(source_file_path):
        raise FileNotFoundError(f"Source file not found: {source_file_path}")

    filename = os.path.basename(source_file_path)

    if snippet.is_bundle:
        dest_dir = snippet.folder_path
        dest_file = os.path.join(dest_dir, filename)
        shutil.copy2(source_file_path, dest_file)
    else:
        # Convert standalone file into a bundle directory
        parent_dir = snippet.folder_path
        stem = os.path.splitext(os.path.basename(snippet.code_file))[0]
        new_bundle_dir = os.path.join(parent_dir, stem)
        os.makedirs(new_bundle_dir, exist_ok=True)

        # Move existing code file
        new_code_path = os.path.join(new_bundle_dir, os.path.basename(snippet.code_file))
        if os.path.exists(snippet.code_file) and snippet.code_file != new_code_path:
            shutil.move(snippet.code_file, new_code_path)
            snippet.code_file = new_code_path

        # Move existing md file if any
        if snippet.md_file and os.path.exists(snippet.md_file):
            new_md_path = os.path.join(new_bundle_dir, os.path.basename(snippet.md_file))
            if snippet.md_file != new_md_path:
                shutil.move(snippet.md_file, new_md_path)
                snippet.md_file = new_md_path

        # Move existing images if any
        new_images = []
        for img_p in snippet.image_files:
            if os.path.exists(img_p):
                new_img_p = os.path.join(new_bundle_dir, os.path.basename(img_p))
                if img_p != new_img_p:
                    shutil.move(img_p, new_img_p)
                new_images.append(new_img_p)
        snippet.image_files = new_images

        # Move existing companions if any
        new_companions = []
        for comp_p in snippet.companion_files:
            if os.path.exists(comp_p):
                new_comp_p = os.path.join(new_bundle_dir, os.path.basename(comp_p))
                if comp_p != new_comp_p:
                    shutil.move(comp_p, new_comp_p)
                new_companions.append(new_comp_p)
        snippet.companion_files = new_companions

        dest_file = os.path.join(new_bundle_dir, filename)
        shutil.copy2(source_file_path, dest_file)

        snippet.folder_path = new_bundle_dir
        snippet.is_bundle = True
        snippet.key = new_bundle_dir

    snippet.reload()
    return dest_file


def create_snippet_bundle(
    target_collection_dir: str,
    snippet_name: str,
    algo_code: str = "",
    md_content: str = ""
) -> SnippetItem:
    """Creates a new snippet folder inside a collection directory with .algo and .md files."""
    safe_name = re.sub(r"[^\w\-]", "_", snippet_name.strip().lower())
    if not safe_name:
        safe_name = "nouveau_snippet"

    bundle_dir = os.path.join(target_collection_dir, safe_name)
    os.makedirs(bundle_dir, exist_ok=True)

    algo_path = os.path.join(bundle_dir, f"{safe_name}.algo")
    if not algo_code.strip():
        algo_code = f"""ALGORITHME {safe_name.title()}
DEBUT
  # Écrivez votre algorithme ici
  Ecrire("Bonjour depuis {safe_name.title()} !")
FIN

Tableau de déclaration des objets globaux
Objet          Type / Nature
/              /
"""
    with open(algo_path, "w", encoding="utf-8") as f:
        f.write(algo_code)

    md_path = os.path.join(bundle_dir, f"{safe_name}.md")
    if not md_content.strip():
        md_content = f"""# {snippet_name.title()}

## Description
Documentation et explication pour l'algorithme `{safe_name}`.

## Objectif
- Expliquer le fonctionnement de l'algorithme
- Spécifier les entrées et sorties
"""
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_content)

    return SnippetItem(
        key=bundle_dir,
        title=snippet_name.title(),
        category=os.path.basename(target_collection_dir),
        code_file=algo_path,
        code=algo_code,
        folder_path=bundle_dir,
        is_bundle=True,
        desc=f"Snippet {snippet_name}",
        md_file=md_path,
        image_files=[],
        companion_files=[]
    )
