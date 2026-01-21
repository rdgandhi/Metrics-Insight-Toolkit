# DAX Measures (Merchandising KPIs)

## Core
Sales $ = SUM(FactSales[Sales])
Units = SUM(FactSales[Units])
Orders = DISTINCTCOUNT(FactSales[OrderID])
AOV = DIVIDE([Sales $], [Orders])

GM $ = SUM(FactSales[GrossMarginAmt])
GM % = DIVIDE([GM $], [Sales $])

Markdown $ = SUM(FactSales[DiscountAmt])
Gross Sales $ = [Sales $] + [Markdown $]
Markdown Rate % = DIVIDE([Markdown $], [Gross Sales $])

On Hand Units = SUM(FactInventorySnapshot[OnHandUnits])
Sell-through % = DIVIDE([Units], [Units] + [On Hand Units])

Weekly Units =
CALCULATE(
    [Units],
    ALLEXCEPT(DimDate, DimDate[WeekStart])
)

Avg Weekly Units = AVERAGEX(VALUES(DimDate[WeekStart]), [Weekly Units])

WOS = DIVIDE([On Hand Units], [Avg Weekly Units])

Stockout Days =
COUNTROWS(
    FILTER(
        VALUES(DimDate[Date]),
        CALCULATE([On Hand Units]) = 0
    )
)
