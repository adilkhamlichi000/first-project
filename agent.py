import sys

from agents import Agent, Runner, WebSearchTool


stock_analyst = Agent(
    name="Stock Analyst",
    model="gpt-5.6-luna",
    instructions="""
You are a cautious equity-research screening agent.

Your job is to decide whether a listed company deserves deeper investment research.

For every company:
1. Use web search to find the latest reliable information, prioritizing company investor-relations pages, regulatory filings, and other primary sources.
2. Review the business, latest financial results, profitability, balance-sheet/capital strength, valuation clues, important catalysts, and main risks.
3. Cross-check important claims when possible.
4. Clearly label rough calculations, estimates, and missing information.
5. Do not invent figures. If reliable current data is unavailable, say so.
6. Finish with one screening verdict: DEEPER RESEARCH, PASS FOR NOW, or INSUFFICIENT INFORMATION.
7. Explain the verdict concisely and include source links/citations in the final answer.

This is research assistance, not personalized investment advice.
""",
    tools=[WebSearchTool(search_context_size="medium")],
)


def main():
    company = " ".join(sys.argv[1:]).strip()
    if not company:
        company = input("Company to analyse: ").strip()

    if not company:
        raise SystemExit("Please provide a company name.")

    task = f"""
Analyse {company} as an equity-research screening candidate.
Use current information and perform whatever web searches are needed.
Give me the most decision-useful facts, risks, and a clear screening verdict.
"""

    result = Runner.run_sync(stock_analyst, task)
    print("\n" + result.final_output)


if __name__ == "__main__":
    main()
