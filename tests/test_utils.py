import inspect
import dashboard_utils

def assert_returned_tables_sort_order(dashboard_module):
    """
    Dynamically calls a dashboard's update_dashboard callback, finds all returned 
    tables, extracts their headers, and verifies they are returned in the 
    canonical order defined by dashboard_utils.
    """
    # 1. Dynamically figure out the callback arguments and pass None for all of them
    update_func = dashboard_module.update_dashboard
    
    # Unpack the function if it's wrapped by the @callback decorator
    func_to_inspect = getattr(update_func, '__wrapped__', update_func)
    sig = inspect.signature(func_to_inspect)
    kwargs = {param: None for param in sig.parameters}
    
    # Execute the callback to get the returned tuple of figures and tables
    result = update_func(**kwargs)
    
    # Ensure result is iterable
    if not isinstance(result, (list, tuple)):
        result = [result]
        
    returned_labels = []
    
    # 2. Iterate through the returned objects and extract the headers of any tables
    for item in result:
        # Check if the returned item is a Dash Table component
        if getattr(item, 'component_name', '') == 'Table':
            try:
                # dbc.Table.from_dataframe creates a structure like: 
                # children=[Thead(children=[Tr(children=[Th(label), Th(count)])]), Tbody(...)]
                for child in getattr(item, 'children', []):
                    if getattr(child, 'component_name', '') == 'Thead':
                        # Navigate down the DOM tree to the first column's text
                        tr = child.children[0]
                        first_th = tr.children[0]
                        label = first_th.children
                        
                        if isinstance(label, str):
                            returned_labels.append(label)
                        break
            except (IndexError, AttributeError, TypeError):
                continue
                
    # 3. Calculate what the expected order should be using dashboard_utils ranking
    def get_rank(label):
        norm = dashboard_utils._normalize_filter_label(label)
        return dashboard_utils._RIGHT_TABLE_LABEL_RANK.get(
            norm, 
            len(dashboard_utils._RIGHT_TABLE_LABEL_RANK) # Fallback rank
        )
        
    expected_labels = sorted(returned_labels, key=get_rank)
    
    # 4. Assert the tables were returned in the correct canonical order
    assert returned_labels == expected_labels, (
        f"Tables returned by update_dashboard are out of standard order.\n"
        f"Expected (based on dashboard_utils): {expected_labels}\n"
        f"Actual order returned:               {returned_labels}"
    )