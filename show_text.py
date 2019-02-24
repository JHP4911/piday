import subprocess
LINE_LENGTH = 14
LINES = 6
PAD_LINES = ['', '', '', '', '', '', '']
def show_text(text):
  words = text.split(' ')
  tokens = []
  for word in words:
    tokens += list(chunkstring(word, LINE_LENGTH))

  lines = []
  line = ''
  for word in tokens:
    if len(word) + len(line) >= LINE_LENGTH:
      lines.append(line)
      line = ''
    if len(line) == 0:
      line = word
    else:
      line = line + ' ' + word
  if len(line) > 0:
    lines.append(line)
    
  print_lines(lines)

def chunkstring(string, length):
    return (string[0+i:length+i] for i in range(0, len(string), length))

def print_lines(text):
  lines = PAD_LINES + text
  lines = lines[-LINES:] 
  command = ['./showtext']+lines
  subprocess.call(command)

if __name__  == "__main__":
	show_text('123456789012345 that is some long text')
