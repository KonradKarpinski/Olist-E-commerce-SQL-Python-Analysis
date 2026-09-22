Task 5: Sales & Payments Dashboard

Sales and Payments Dataset:

```powerquery
let
    Source = Csv.Document(File.Contents("C:\Users\User\Desktop\olist_orders_cleaned.csv"),[Delimiter=",", Columns=8, Encoding=1250, QuoteStyle=QuoteStyle.None]),
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{{"order_id", type text}, {"customer_id", type text}, {"order_status", type text}, {"order_purchase_timestamp", type datetime}, {"order_approved_at", type datetime}, {"order_delivered_carrier_date", type datetime}, {"order_delivered_customer_date", type datetime}, {"order_estimated_delivery_date", type datetime}}),
    #"Filtered Rows" = Table.SelectRows(#"Changed Type", each ([order_status] = "delivered")),
    #"Merged Queries" = Table.NestedJoin(#"Filtered Rows", {"order_id"}, olist_order_payments_cleaned, {"order_id"}, "olist_order_payments_cleaned", JoinKind.Inner),
    #"Extracted Date" = Table.TransformColumns(#"Merged Queries",{{"order_purchase_timestamp", DateTime.Date, type date}}),
    #"Inserted Year" = Table.AddColumn(#"Extracted Date", "Year", each Date.Year([order_purchase_timestamp]), Int64.Type),
    #"Inserted Month Name" = Table.AddColumn(#"Inserted Year", "Month Name", each Date.MonthName([order_purchase_timestamp]), type text),
    #"Inserted Month" = Table.AddColumn(#"Inserted Month Name", "Month", each Date.Month([order_purchase_timestamp]), Int64.Type),
    #"Expanded olist_order_payments_cleaned" = Table.ExpandTableColumn(#"Inserted Month", "olist_order_payments_cleaned", {"order_id", "payment_sequential", "payment_type", "payment_installments", "payment_value"}, {"olist_order_payments_cleaned.order_id", "olist_order_payments_cleaned.payment_sequential", "olist_order_payments_cleaned.payment_type", "olist_order_payments_cleaned.payment_installments", "olist_order_payments_cleaned.payment_value"}),
    #"Removed Other Columns" = Table.SelectColumns(#"Expanded olist_order_payments_cleaned",{"Month", "Month Name", "Year", "olist_order_payments_cleaned.payment_value", "olist_order_payments_cleaned.payment_type"}),
    #"Renamed Columns" = Table.RenameColumns(#"Removed Other Columns",{{"Month", "Sales Month Number"}, {"Month Name", "Sales Month"}, {"Year", "Sales Year"}, {"olist_order_payments_cleaned.payment_value", "Payment Value"}, {"olist_order_payments_cleaned.payment_type", "Payment Type"}}),
    #"Changed Payment Value to number" = Table.TransformColumnTypes(#"Renamed Columns",{{"Payment Value", type number}}),
    #"Reordered Columns" = Table.ReorderColumns(#"Changed Payment Value to number",{"Sales Year", "Sales Month Number", "Sales Month", "Payment Type", "Payment Value"}),
    #"Replaced Value - Credit Card" = Table.ReplaceValue(#"Reordered Columns","credit_card","Credit Card",Replacer.ReplaceText,{"Payment Type"}),
    #"Replaced Value - Voucher" = Table.ReplaceValue(#"Replaced Value - Credit Card","voucher","Voucher",Replacer.ReplaceText,{"Payment Type"}),
    #"Replaced Value - Boleto" = Table.ReplaceValue(#"Replaced Value - Voucher","boleto","Boleto",Replacer.ReplaceText,{"Payment Type"}),
    #"Replaced Value - Debit Card" = Table.ReplaceValue(#"Replaced Value - Boleto","debit_card","Debit Card",Replacer.ReplaceText,{"Payment Type"})
in
    #"Replaced Value - Debit Card"
```

Task 6: Dynamic Shipping Cost Simulator

olist_orders_cleaned:

```powerquery
let
    Source = Csv.Document(File.Contents("C:\Users\User\Desktop\olist_orders_cleaned.csv"),[Delimiter=",", Columns=8, Encoding=1252, QuoteStyle=QuoteStyle.None]),
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{{"order_id", type text}, {"customer_id", type text}, {"order_status", type text}, {"order_purchase_timestamp", type datetime}, {"order_approved_at", type datetime}, {"order_delivered_carrier_date", type datetime}, {"order_delivered_customer_date", type datetime}, {"order_estimated_delivery_date", type datetime}}),
    #"Filtered Rows" = Table.SelectRows(#"Changed Type", each ([order_status] = "delivered"))
in
    #"Filtered Rows"
```

Shipping Cost Dataset:

```powerquery
let
    Source = Table.NestedJoin(olist_orders_cleaned, {"order_id"}, olist_order_items_cleaned, {"order_id"}, "olist_order_items_cleaned", JoinKind.Inner),
    #"Merged Queries" = Table.NestedJoin(Source, {"customer_id"}, olist_customers_cleaned, {"customer_id"}, "olist_customers_cleaned", JoinKind.Inner),
    #"Expanded olist_order_items_cleaned" = Table.ExpandTableColumn(#"Merged Queries", "olist_order_items_cleaned", {"freight_value"}, {"olist_order_items_cleaned.freight_value"}),
    #"Expanded olist_customers_cleaned" = Table.ExpandTableColumn(#"Expanded olist_order_items_cleaned", "olist_customers_cleaned", {"customer_state"}, {"olist_customers_cleaned.customer_state"}),
    #"Removed Other Columns" = Table.SelectColumns(#"Expanded olist_customers_cleaned",{"olist_order_items_cleaned.freight_value", "olist_customers_cleaned.customer_state"}),
    #"Reordered Columns" = Table.ReorderColumns(#"Removed Other Columns",{"olist_customers_cleaned.customer_state", "olist_order_items_cleaned.freight_value"}),
    #"Renamed Columns" = Table.RenameColumns(#"Reordered Columns",{{"olist_customers_cleaned.customer_state", "Customer State"}, {"olist_order_items_cleaned.freight_value", "Shipping Cost"}})
in
    #"Renamed Columns"
```
