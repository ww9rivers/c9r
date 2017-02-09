# coding: utf8
#
# This program is licensed under the GPL v3.0, which is found at the URL below:
#      http://opensource.org/licenses/gpl-3.0.html
#
# Copyright (c) 2011, 9Rivers.net, LLC. All rights reserved.
#
# Redistribution and use in source and binary forms are permitted
# provided that this notice is preserved and that due credit is given
# to the copyright holders listed above. The name of the copyright holders
# may not be used to endorse or promote products derived from this
# software without specific prior written permission. This software
# is provided ``as is'' without express or implied warranty.
#

def ui_grid_page (xopt, xtsql, xrsql, xrow2cell = 'ui_grid_row2cell', xdefs = False):
    """
    Generate a page of data for a grid.

    @param	xopt	Options to use
    @param	xtsql	SQL statement to get a total count of rows
    @param	xrsql	SQL statement to get the rows
    @param	xdefs	Default options to use
    @return	An array of jQuery grid cells.
    """
    xrows = 20
    xpage = 1
    xsidx = false
    xsord = 'ASC'
    if not empty(xdefs): extract(xdefs, EXTR_IF_EXISTS)
    extract(xopt, EXTR_IF_EXISTS)
    xtotal = db_count_rows(xtsql)
    xlastpage = ceil(xtotal/xrows)
    if xpage > xlastpage: xpage = xlastpage
    elif xpage < 1: xpage = 1

    xres = db_query(xrsql += (" ORDER BY `%s` %s" % (xsidx, xsord) if xsidx else "") + (" LIMIT %d,%d" % ((xpage-1)*xrows,xrows)))
    if not xres:
        drupal_json(array
                    ('status' => 'failure',
                     'data' => t('Error retrieving data.'),
                     'debug' => array
                     (
                    'SQL' => xrsql
                    )
                     ))
        return

    xdata = []
    for (xxcnt = 0 xrow = db_fetch_object(xres) xxcnt++):
        xdata[] = call_user_func_array(xrow2cell, array(&xrow))

    drupal_json(array
		    ('page' => xpage, 'total' => xlastpage, 'records' => xxcnt, 'rows' => xdata,
		     // 'sql' => xrsql,
		    ))
}


/**	Default callback to convert an SQL value array to a jqGrid cell array.
 *
 * @param	xrow	Reference to one row in the SQL query result.
 * @return	An array representing a jqGrid row.
 */
function c9r_ui_grid_row2cell (&xrow)
{
	return array('cell' => array_values((array)xrow) )
}
