from Pyro4 import expose

class Solver:
    def __init__(self, workers=None, input_file_name=None, output_file_name=None):
        self.input_file_name = input_file_name
        self.output_file_name = output_file_name
        self.workers = workers
        print("Inited")

    def solve(self):
        print("Job Started")
        print("Workers %d" % len(self.workers))

        point, lines = self.read_input()

        total_lines = len(lines)
        divided_lines = []
        lines_per_part = total_lines // len(self.workers)
        remaining_lines = total_lines % len(self.workers)

        start = 0
        for i in xrange(len(self.workers)):
            end = start + lines_per_part + (1 if i < remaining_lines else 0)
            divided_lines.append(lines[start:end])
            start = end

        points = set()
        for line in lines:
            points.add(line[0])
            points.add(line[1])

        # Sort points based on y-coordinates
        points = sorted(points, key=lambda p: p[1])

        strips = []
        for i in xrange(len(points) - 1):
            strips.append((points[i][1], points[i + 1][1]))

        # Identify the strip for the given point
        strip = None
        for i, (y1, y2) in enumerate(strips):
            if y1 <= point[1] <= y2:
                strip = (y1, y2)
                break

        mapped = []
        for i in xrange(len(divided_lines)):
            result = self.workers[i].mymap(point, divided_lines[i], strip)
            mapped.append(result)

        res_lines = self.myreduce(mapped)

        left_line, right_line = Solver.find_bounding_lines_and_x_at_y(res_lines, point)


        self.write_output(point, strip, res_lines, left_line, right_line)

    @staticmethod
    @expose
    def mymap(point, lines, strip):
        return Solver.find_lines_in_strip(point, lines, strip)

    @staticmethod
    @expose
    def myreduce(mapped):
        print("reduce")

        flattened_list = []
        for sublist in mapped:
            for item in sublist.value:
                flattened_list.append(item)

        return flattened_list

    @staticmethod
    @expose
    def line_eq(point1, point2):
        x1, y1 = point1
        x2, y2 = point2
        if x1 == x2:  # Vertical line
            return 0, y2
        m = (y2 - y1) / (x2 - x1)
        c = y1 - m * x1
        return m, c

    @staticmethod
    @expose
    def find_lines_in_strip(point, lines, strip):
        strip_bottom = strip[0]
        strip_top = strip[1]
        lines_in_strip = []
        for i, line in enumerate(lines):
            m, c = Solver.line_eq(line[0], line[1])
            # Calculate intersection points with strip bottom and top
            x_bottom = (strip_bottom - c) / m if m != 0 else None
            x_top = (strip_top - c) / m if m != 0 else None

            # Check if both x_bottom and x_top are within the range of x_coords
            if x_bottom is not None and min(line[0][0], line[1][0]) <= x_bottom <= max(line[0][0], line[1][0]) \
                    and x_top is not None and min(line[0][0], line[1][0]) <= x_top <= max(line[0][0], line[1][0]):
                lines_in_strip.append(line)
        return lines_in_strip

    @staticmethod
    @expose
    def find_bounding_lines_and_x_at_y(lines_in_strip, point):
        x_at_y = []
        left_line, right_line = None, None

        for line in lines_in_strip:
            (x1, y1), (x2, y2) = line
            if y1 == y2:
                x_at_y.append((line, min(x1, x2)))
            elif y1 <= point[1] <= y2 or y2 <= point[1] <= y1:
                x_at_y.append((line, x1 + (point[1] - y1) * (x2 - x1) / (y2 - y1)))

        x_at_y.sort(key=lambda x: x[1])

        for i in xrange(len(x_at_y) - 1):
            if x_at_y[i][1] <= point[0] <= x_at_y[i + 1][1]:
                left_line, right_line = x_at_y[i][0], x_at_y[i + 1][0]
                break

        return left_line, right_line

    def read_input(self):
        with open(self.input_file_name, 'r') as file:
            lines = []
            point = None
            for line in file:
                parts = line.strip().split()
                if len(parts) == 2:
                    point = (int(parts[0]), int(parts[1]))
                elif len(parts) == 4:
                    lines.append(((int(parts[0]), int(parts[1])), (int(parts[2]), int(parts[3]))))
        return point, lines

    def write_output(self, point, strip, lines_in_strip, left_line, right_line):
        with open(self.output_file_name, 'w') as f:
            f.write("Point (" + str(point[0]) + ","+ str(point[1]) + ") lies in strip y=" + str(strip[0]) + " and y=" + str(strip[1]) + "\n" )
            #f.write("Lines that lie in strip: " + "\n")
            #for line in lines_in_strip:
            #    f.write("["+str(line[0]) + " , " + str(line[1]) + "] , ")
            #f.write("\n")
            f.write("Point (" + str(point[0]) + ","+ str(point[1]) + ") lies between lines "+"(" + str(left_line[0][0]) + "," + str(left_line[0][1]) + "),(" + str(left_line[1][0])+ "," + str(left_line[1][1]) + ")" + " and " + "(" +str(right_line[0][0]) + ","+ str(right_line[0][1]) + "),(" + str(right_line[1][0]) + "," + str(right_line[1][1]) + ")")



