from dollarxpy import custom_element, BasicPath

element = BasicPath(xpath='*', xpath_explanation='any element')
div = custom_element('div')
span = custom_element('span')
image = custom_element('image')
button = custom_element('button')

li = BasicPath(xpath='li', xpath_explanation='list item')
ul = BasicPath(xpath='ul', xpath_explanation='unordered list')
ol = BasicPath(xpath='ol', xpath_explanation='ordered list')
select = BasicPath(xpath='select', xpath_explanation='selection menu')
html = BasicPath(xpath='html', xpath_explanation='document')
body = BasicPath(xpath='body', xpath_explanation='document body')
section = custom_element("section")

header1 = BasicPath(xpath='h1', xpath_explanation='header-1')
header2 = BasicPath(xpath='h2', xpath_explanation='header-2')
header3 = BasicPath(xpath='h3', xpath_explanation='header-3')
header4 = BasicPath(xpath='h4', xpath_explanation='header-4')
header5 = BasicPath(xpath='h5', xpath_explanation='header-5')
header6 = BasicPath(xpath='h6', xpath_explanation='header-6')
header = header1.or_(header2).or_(header3).or_(header4).or_(header5).or_(header6)

input = custom_element("input")
form = custom_element("form")
title = custom_element("title")
iframe = custom_element("iframe")

table = custom_element("table")
td = BasicPath(xpath='td', xpath_explanation='table cell')
tr = BasicPath(xpath='td', xpath_explanation='table row')
th = BasicPath(xpath='th', xpath_explanation='table header')

option = custom_element("option")
label = custom_element("label")
