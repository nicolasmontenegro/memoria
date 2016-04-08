import math

def countPage(page, totalfound, resultsperpage):
	totalpages = math.ceil(totalfound/resultsperpage)
	rangepage = []
	sub = 0
	pos = 0
	if page-3 < 1:
		pos = (page-3) * -1
	if page+2 > totalpages:
		sub = totalpages - (page+2)
	for item in range(page-2+sub, page+3+pos):
		if item > 0 and item <= totalpages:
			rangepage.append(item)
	prevpage = page - 1
	nextpage = page + 1
	if prevpage < 1:
		prevpage = -1
	if nextpage > totalpages:
		nextpage = -1
	return {
		'rangepage': rangepage,
		'thispage': page,
		'prevpage': prevpage,
		'nextpage': nextpage,
		'totalpages': totalpages}

