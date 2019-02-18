import os


class Enumerate:

	def __init__(self):
		self._MARKDOWN = os.path.join(os.path.dirname(__file__), "index.md")
		self._TARGET   = os.path.join(os.path.dirname(__file__), "index00.md")
		self.map = {}
		self.lines_modified = {}   # {position: Int, content: String}

	def enumerate_md(self):
		with open(self._MARKDOWN, 'r') as f:
			position = 0
			while 'end of file is not reached':
				line = f.readline()
				if line == "":
					break

				line_stripped = line.strip()
				
				if len(line_stripped) > 0 and line_stripped[0] == '#':
					hash_num = 0
					while line_stripped[hash_num] == '#':
						hash_num += 1

					prefix = "".join(["#" for i in range(0, hash_num)])
					number_str = self._get_number(prefix)
					self._append_line(position, number_str, prefix, line)

				position += 1

		self._update_file()

	
	def _get_number(self, prefix):
		self._update_map(prefix)
		number_str = ""
		for key in self.map:
			number_str += str(self.map[key]) + "."

		return number_str[:-1]


	def _update_map(self, prefix):
		if len(prefix) not in self.map:
			for i in range(1, len(prefix) + 1):
				if i not in self.map:
					self.map[i] = 1

		else:
			self.map[len(prefix)] += 1
			del_keys = []
			for key in self.map:
				if key > len(prefix):
					del_keys.append(key)

			for key in del_keys:
				self.map.pop(key, None)


	def _append_line(self, ind, number, prefix, line):
		line_split = line.split(prefix) 
		self.lines_modified[ind] = prefix + " " + number + " " + line_split[1]


	def _update_file(self):
		with open(self._MARKDOWN, 'r') as f:
			with open(self._TARGET, 'a') as ft:
				position = 0
				while 'end of file is not reached':
					line = f.readline()
					if line == '':
						break

					if position in self.lines_modified:
						ft.write(self.lines_modified[position])
					else:
						ft.write(line)

					position += 1

		os.remove(self._MARKDOWN)
		os.rename(self._TARGET, self._MARKDOWN)





if __name__ == '__main__':
	Enumerate().enumerate_md()