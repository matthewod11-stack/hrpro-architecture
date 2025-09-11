from app.advisor.prompts import get_cpo_system_prompt


def test_get_cpo_system_prompt_replaces_org():
    org = "Acme"
    prompt = get_cpo_system_prompt(org)
    assert "Acme" in prompt
    assert "<XXXXX>" not in prompt
    assert prompt.startswith("You are the Chief People Officer at Acme")


def test_get_cpo_system_prompt_default():
    prompt = get_cpo_system_prompt(None)
    assert "your organization" in prompt
    assert "<XXXXX>" not in prompt
    assert prompt.startswith("You are the Chief People Officer at your organization")
