from agentprobe_engine.rules import check_rules


def test_all_required_terms_present_and_no_forbidden_terms() -> None:
    case = {"must_contain": ["75", "attendance"], "must_not_contain": ["65"]}

    result = check_rules(case, "At least 75 percent attendance is required.")

    assert result == {"passed": True, "missing": [], "forbidden_found": []}


def test_missing_required_term() -> None:
    case = {"must_contain": ["75", "exam"], "must_not_contain": []}

    result = check_rules(case, "You need 75 percent.")

    assert result == {"passed": False, "missing": ["exam"], "forbidden_found": []}


def test_forbidden_term_found() -> None:
    case = {"must_contain": ["75"], "must_not_contain": ["65", "60"]}

    result = check_rules(case, "You need 65 percent, not 75 percent.")

    assert result == {"passed": False, "missing": [], "forbidden_found": ["65"]}


def test_checks_are_case_insensitive() -> None:
    case = {"must_contain": ["ATTENDANCE"], "must_not_contain": ["FAIL"]}

    result = check_rules(case, "attendance is required, not fail")

    assert result == {"passed": False, "missing": [], "forbidden_found": ["FAIL"]}


def test_missing_and_empty_term_lists_are_safe() -> None:
    assert check_rules({}, "anything") == {
        "passed": True,
        "missing": [],
        "forbidden_found": [],
    }
    assert check_rules(
        {"must_contain": [], "must_not_contain": []},
        "anything",
    ) == {"passed": True, "missing": [], "forbidden_found": []}
    assert check_rules(
        {"must_contain": None, "must_not_contain": None},
        "anything",
    ) == {"passed": True, "missing": [], "forbidden_found": []}
