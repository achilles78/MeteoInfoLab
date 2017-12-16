#-----------------------------------------------------
# Author: Yaqiang Wang
# Date: 2014-12-27
# Purpose: MeteoInfo table module
# Note: Jython
#-----------------------------------------------------

import datetime

from org.meteoinfo.data import TableData, TimeTableData, ArrayMath, ArrayUtil, TableUtil, DataTypes

import miarray
from miarray import MIArray
import mipylib.miutil as miutil

from java.util import Calendar, Date

###############################################################        
#  The encapsulate class of TableData
class PyTableData():
    # Must be a TableData object
    def __init__(self, data=None):
        self.data = data
        if data is None:
            self.data = TableData()
        self.timedata = isinstance(data, TimeTableData)
        
    def __getitem__(self, key):
        if isinstance(key, (str, unicode)):     
            coldata = self.data.getColumnData(key)
            if coldata.getDataType().isNumeric():
                return MIArray(ArrayUtil.array(coldata.getDataValues()))
            elif coldata.getDataType() == DataTypes.Date:
                vv = coldata.getData()
                r = []
                cal = Calendar.getInstance()
                for v in vv:
                    cal.setTime(v)
                    year = cal.get(Calendar.YEAR)
                    month = cal.get(Calendar.MONTH) + 1
                    day = cal.get(Calendar.DAY_OF_MONTH)
                    hour = cal.get(Calendar.HOUR_OF_DAY)
                    minute = cal.get(Calendar.MINUTE)
                    second = cal.get(Calendar.SECOND)
                    dt = datetime.datetime(year, month, day, hour, minute, second)
                    r.append(dt)
                return r
            else:
                return MIArray(ArrayUtil.array(coldata.getData()))
        else:
            row = key[0]
            col = key[1]
            return self.data.getValue(row, col)
        return None
        
    def __setitem__(self, key, value):
        if isinstance(value, MIArray):
            self.data.setColumnData(key, value.aslist())
        else:
            self.data.setColumnData(key, value)
            
    def __repr__(self):
        return self.data.toString()
        
    def rownum(self):
        '''
        Returns the row number.
        '''
        return self.data.getDataTable().getRowCount()
        
    def colnum(self):
        '''
        Returns the column number.
        '''
        return self.data.getDataTable().getColumnCount()
    
    def colnames(self):
        '''
        Returns the column names.
        '''
        return self.data.getDataTable().getColumnNames()
        
    def setcolname(self, col, colname):
        '''
        Set column name to a specified column.
        
        :param col: (*int*) Column index.
        :param colname: (*string*) New column name.
        '''
        self.data.getDataTable().renameColumn(col, colname)
        
    def setcolnames(self, colnames):
        '''
        Set column names to all or first part of columns.
        
        :param colnames: (*list*) List of the column names.
        '''
        for i in range(len(colnames)):
            self.data.getDataTable().renameColumn(i, colnames[i])
    
    def coldata(self, key):
        '''
        Return column data as one dimension array.
        
        :param key: (*string*) Column name.
        
        :returns: (*MIArray*) Colomn data.
        '''
        if isinstance(key, str):
            print key     
            values = self.data.getColumnData(key).getDataValues()
            return MIArray(ArrayUtil.array(values))
        return None
        
    def getvalue(self, row, col):
        '''
        Return a value in the table.
        
        :param row: (*int*) Row index.
        :param col: (*int*) Column index.
        
        :returns: The value at the row and column.
        '''
        r = self.data.getValue(row, col)
        if isinstance(r, Date):
            r = miutil.pydate(r)
        return r

    def setvalue(self, row, col, value):
        '''
        Set a value to the table.
        
        :param row: (*int*) Row index.
        :param col: (*int*) Column index.
        :param value: (*object*) The value.
        '''
        self.data.setValue(row, col, value)
    
    def addcoldata(self, colname, dtype, coldata):
        '''
        Add a column and its data.
        
        :param colname: (*string*) The new column name.
        :param dtype: (*string*) The data type. [string | int | float].
        :param value: (*array_like*) The data value.
        '''
        if isinstance(coldata, MIArray):
            self.data.addColumnData(colname, dtype, coldata.aslist())
        else:
            self.data.addColumnData(colname, dtype, coldata)

    def addcol(self, colname, dtype, index=None):
        '''
        Add an emtpy column.
        
        :param colname: (*string*) The new column name.
        :param dtype: (*string*) The data type. [string | int | float].
        :param index: (*int*) The order index of the column to be added. Default is ``None``, the
            column will be added as last column.
        '''
        dtype = TableUtil.toDataTypes(dtype)
        if index is None:
            self.data.addColumn(colname, dtype)
        else:
            self.data.addColumn(index, colname, dtype)
    
    def delcol(self, colname):
        '''
        Delete a column.
        
        :param colname: (*string*) The column name.
        '''
        self.data.removeColumn(colname)
        
    def addrow(self, row=None):
        '''
        Add a row.
        
        :param row: (*DataRow*) The row. Default is ``None`, an emtpy row will be added.
        '''
        if row is None:
            self.data.addRow()
        else:
            self.data.addRow(row)
            
    def addrows(self, rows):
        '''
        Add rows.
        
        :param rows: (*list*) The list of the rows.
        '''
        self.data.addRows(rows)
        
    def delrow(self, row):
        '''
        Delete a row.
        
        :param row: (*int or DataRow*) Data row.
        '''
        self.data.dataTable.removeRow(row)
        
    def delrows(self, rows):
        '''
        Delete rows.
        
        :param rows: (*list*) Data rows.
        '''
        self.data.dataTable.removRows(rows)
        
    def clearrows(self):
        '''
        Clear all rows.               
        '''
        self.data.dataTable.getRows().clear()
        
    def getrow(self, index):
        '''
        Return a row.
        
        :param index: (*int*) Row index.
        
        :returns: The row
        '''
        return self.data.getRow(index)
        
    def getrows(self):
        '''
        Return all rows.               
        '''
        return self.data.getRows()
        
    #Set time column
    def timecol(self, colname):
        '''
        Set time column.
        
        :param colname: (*string*) The Name of the column which will be set as time column. For time
            statistic calculation such as daily average.
        '''
        tdata = TimeTableData(self.data.dataTable)
        tdata.setTimeColName(colname)
        self.data = tdata;
        self.timedata = True
        
    def join(self, other, colname, colname1=None):
        '''
        Join with another table. Joining data is typically used to append the fields of one table to 
        those of another through an attribute or field common to both tables.
        
        :param other: (*PyTableData*) The other table.
        :param colname: (*string*) The common field name.
        :param colname1: (*string*) The common field name in the other table. Default is ``None`` if
            the common field names are same in both tables.
        '''
        if colname1 == None:
            self.data.join(other.data, colname)
        else:
            self.data.join(other.data, colname, colname1)
        
    def savefile(self, filename, delimiter=','):
        '''
        Save the table data to an ASCII file.
        
        :param filename: (*string*) The file name.
        :param delimiter: (*string*) Field delimiter character. Default is ``,``.
        '''
        if delimiter == ',':
            self.data.saveAsCSVFile(filename)
        else:
            self.data.saveAsASCIIFile(filename)
            
    def ave(self, colnames):
        '''
        Average some columns data.
        
        :param colnames: (*list*) Column names.
        
        :returns: (*PyTableData*) Result table contains one row of average data of the columns.
        '''
        cols = self.data.findColumns(colnames)
        dtable = self.data.average(cols)
        return PyTableData(TableData(dtable))
        
    def ave_year(self, colnames, year=None):
        '''
        Yearly average function. Time column is needed.
        
        :param colnames: (*list*) Column names.
        :param year: (*int*) Specific year. Default is ``None``.
        
        :returns: (*PyTableData*) Result table contains some rows of yearly average data of the columns.
        '''
        if not self.timedata:
            print 'There is no time column!'
            return None
        else:
            cols = self.data.findColumns(colnames)
            if year is None:
                dtable = self.data.ave_Year(cols)
            else:
                dtable = self.data.ave_Year(cols, year)
            return PyTableData(TableData(dtable))
            
    def ave_yearmonth(self, colnames, month):
        '''
        Average the table data by year and month. Time column is needed.
        
        :param colnames: (*list*) Column names.
        :param month: (*int*) Specific month.
        
        :returns: (*PyTableData*) Result table contains some rows of year-month average data of the columns.
        '''
        if not self.timedata:
            print 'There is no time column!'
            return None
        else:
            cols = self.data.findColumns(colnames)
            dtable = self.data.ave_YearMonth(cols, month)
            return PyTableData(TableData(dtable))
                  
    def ave_monthofyear(self, colnames):
        '''
        Month of year average function. Time column is needed.
        
        :param colnames: (*list*) Column names.
        
        :returns: (*PyTableData*) Result table contains some rows of month of year average data of the columns.
        '''
        if not self.timedata:
            print 'There is no time column!'
            return None
        else:
            cols = self.data.findColumns(colnames)
            dtable = self.data.ave_MonthOfYear(cols)
            return PyTableData(TableData(dtable))
            
    def ave_seasonofyear(self, colnames):
        '''
        Season of year average function. Time column is needed.
        
        :param colnames: (*list*) Column names.
        
        :returns: (*PyTableData*) Result table contains some rows of season of year average data of the columns.
        '''
        if not self.timedata:
            print 'There is no time column!'
            return None
        else:
            cols = self.data.findColumns(colnames)
            dtable = self.data.ave_SeasonOfYear(cols)
            return PyTableData(TableData(dtable))
            
    def ave_hourofday(self, colnames):
        '''
        Hour of day average function. Time column is needed.
        
        :param colnames: (*list*) Column names.
        
        :returns: (*PyTableData*) Result table contains some rows of hour of day average data of the columns.
        '''
        if not self.timedata:
            print 'There is no time column!'
            return None
        else:
            cols = self.data.findColumns(colnames)
            dtable = self.data.ave_HourOfDay(cols)
            return PyTableData(TableData(dtable))
    
    def ave_month(self, colnames):
        '''
        Monthly average function. Time column is needed.
        
        :param colnames: (*list*) Column names.
        
        :returns: (*PyTableData*) Result table contains some rows of monthly average data of the columns.
        '''
        if not self.timedata:
            print 'There is no time column!'
            return None
        else:
            cols = self.data.findColumns(colnames)
            dtable = self.data.ave_Month(cols)
            return PyTableData(TableData(dtable))
            
    def ave_day(self, colnames, day=None):
        '''
        Daily average function. Time column is needed.
        
        :param colnames: (*list*) Column names.
        
        :returns: (*PyTableData*) Result table contains some rows of daily average data of the columns.
        '''
        if not self.timedata:
            print 'There is no time column!'
            return None
        else:
            cols = self.data.findColumns(colnames)
            dtable = self.data.ave_Day(cols)
            ttd = TimeTableData(dtable)
            ttd.setTimeColName('Date')
            return PyTableData(ttd)
            
    def ave_hour(self, colnames):
        '''
        Hourly average function. Time column is needed.
        
        :param colnames: (*list*) Column names.
        
        :returns: (*PyTableData*) Result table contains some rows of hourly average data of the columns.
        '''
        if not self.timedata:
            print 'There is no time column!'
            return None
        else:
            cols = self.data.findColumns(colnames)
            dtable = self.data.ave_Hour(cols)
            ttd = TimeTableData(dtable)
            ttd.setTimeColName('Date')
            return PyTableData(ttd)
            
    def assinglerow(self):
        '''
        Returns single row table if this table is single column table.
        '''
        return PyTableData(TableData(self.data.toSingleRowTable(self.data.getDataTable())))
        
    def sql(self, expression):
        '''
        Returns SQL selection result.
        
        :param expression: (*string*) SQL expression.
        
        :returns: (*PyTableData*) SQL result table.
        '''
        return PyTableData(self.data.sqlSelect(expression))
    
    def clone(self):
        '''
        Return coloned table.
        '''
        return PyTableData(self.data.clone())

#################################################################  