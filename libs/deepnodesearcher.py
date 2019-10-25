
def find_element(element, definitions):
	for node_def in definitions:
		element = soup.find(node_def['tag'], class_=node_def['class'])
	return element