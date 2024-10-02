import sys

def main():
	if len(sys.argv) != 4:
		sys.exit("Must have 3 arguments.")

	filename = sys.argv[1]
	x_offset = float(sys.argv[2])
	y_offset = float(sys.argv[3])

	if x_offset or y_offset:
		...
	else:
		print("No backlash compensation selected.")

if __name__ == "__main__":
	main()