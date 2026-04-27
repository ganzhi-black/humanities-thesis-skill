"""论文文本评估工具

用法：
  python review.py paper.md                  # 评估文件
  python review.py paper.md --format json     # JSON输出（供Agent调用）
  python review.py paper.md --severity error  # 只显示错误级别
  echo "文本内容" | python review.py -        # 从stdin读取

评估维度：
  R1/R3  可信度：编造文献、模糊引用、过度断言
  T      术语：同一概念多种译名混用
  F      格式：脚注、参考文献、标点、标题编号
  S      语体：口语化表述、自称不统一
  L      论证逻辑：句间/段间/章节间论证断裂、只论不证、只证不论
  ST     结构：摘要/关键词/参考文献/论点句缺失

所有检查使用确定性规则（正则匹配、术语表比对），不依赖模型判断。
"""
from __future__ import annotations
import sys, os, json, argparse

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "lib"))
sys.path.insert(0, os.path.dirname(__file__))

from lib.review_rules import run_all_checks, Severity


def _read_input(path: str) -> str:
    """读取待评估文本"""
    if path == "-":
        return sys.stdin.read()
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def _render_text(issues, text: str) -> str:
    """渲染为可读文本报告"""
    if not issues:
        return "✓ 未发现问题。\n"

    error_count = sum(1 for i in issues if i.severity == Severity.ERROR)
    warn_count = sum(1 for i in issues if i.severity == Severity.WARNING)
    info_count = sum(1 for i in issues if i.severity == Severity.INFO)

    lines = [
        f"评估完成：{error_count} 个错误 / {warn_count} 个警告 / {info_count} 个提示",
        f"文本总行数：{len(text.splitlines())}",
        "",
    ]

    severity_icon = {
        Severity.ERROR: "✗ [错误]",
        Severity.WARNING: "⚠ [警告]",
        Severity.INFO: "ℹ [提示]",
    }

    for issue in issues:
        icon = severity_icon.get(issue.severity, "?")
        loc = f"第{issue.line}行" if issue.line else ""
        lines.append(f"{icon} {issue.rule} {loc}")
        lines.append(f"  {issue.message}")
        if issue.context:
            lines.append(f"  上下文：{issue.context}")
        if issue.suggestion:
            lines.append(f"  建议：{issue.suggestion}")
        lines.append("")

    return "\n".join(lines)


def _render_json(issues) -> str:
    """渲染为JSON"""
    return json.dumps(
        {
            "total": len(issues),
            "errors": sum(1 for i in issues if i.severity == Severity.ERROR),
            "warnings": sum(1 for i in issues if i.severity == Severity.WARNING),
            "info": sum(1 for i in issues if i.severity == Severity.INFO),
            "issues": [i.to_dict() for i in issues],
        },
        ensure_ascii=False,
        indent=2,
    )


def review(text: str, min_severity: str = "info") -> list:
    """评估文本，返回问题列表。供Agent以模块方式调用。"""
    issues = run_all_checks(text)

    severity_order = {"error": 0, "warning": 1, "info": 2}
    threshold = severity_order.get(min_severity, 2)
    issues = [
        i for i in issues
        if severity_order.get(i.severity.value, 2) <= threshold
    ]

    return issues


def main():
    parser = argparse.ArgumentParser(description="论文文本评估工具")
    parser.add_argument("input", help="待评估文件路径，或 - 表示stdin")
    parser.add_argument("--format", choices=["text", "json"], default="text",
                        help="输出格式")
    parser.add_argument("--severity", choices=["error", "warning", "info"],
                        default="info", help="最低显示级别")
    args = parser.parse_args()

    text = _read_input(args.input)
    issues = review(text, min_severity=args.severity)

    if args.format == "json":
        print(_render_json(issues))
    else:
        print(_render_text(issues, text))


if __name__ == "__main__":
    main()
