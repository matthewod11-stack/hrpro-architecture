from tools.build_corpus import chunks_from_external


def test_heading_chunking_prefers_content():
    md = """
    # Welcome
    ## Real Section Title
    Some content here.
    ### Subsection
    More details.
    """
    chunks = list(
        chunks_from_external(
            "policies/onboarding.md", md, split_level="h2", max_chars=2000
        )
    )
    assert any("real-section-title" in c["anchor"] for c in chunks)
    assert all("policies/onboarding.md" == c["doc"] for c in chunks)
    assert any("Real Section Title" in c["section"] for c in chunks)


def test_no_heading_fallback():
    md = """
    First line is intro.
    Second line is more info.
    """
    chunks = list(
        chunks_from_external("misc/README.md", md, split_level="h2", max_chars=2000)
    )
    assert all(c["anchor"].startswith("§ext-misc-readme") for c in chunks)
    assert all("First line is intro." in c["section"] for c in chunks)


def test_soft_split_long_sections():
    md = """
    ## Big Section
    """ + (
        "A" * 2500
    )
    chunks = list(
        chunks_from_external("policies/long.md", md, split_level="h2", max_chars=1400)
    )
    assert len(chunks) > 1
    assert chunks[0]["anchor"].endswith(".1")
    assert chunks[1]["anchor"].endswith(".1-b")
    assert "(cont.)" in chunks[1]["section"] or True
