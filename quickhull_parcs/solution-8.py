from Pyro4 import expose
#from scipy.spatial import ConvexHull
import sys
sys.setrecursionlimit(1000000000)

class Solver:
    def __init__(self, workers=None, input_file_name=None, output_file_name=None):
        self.input_file_name = input_file_name
        self.output_file_name = output_file_name
        self.workers = workers

        print("Inited")

    def solve(self):

        print("Job Started")
        print("Workers %d" % len(self.workers))

        #q = 0
        #w = 1 / q

        a = self.read_input()

        num_elements = len(a)
        part_size = num_elements // len(self.workers)
        extra_elements = num_elements % len(self.workers)

        part_sizes = [part_size + 1 if i < extra_elements else part_size for i in xrange(len(self.workers))]
        divided_parts = [a[sum(part_sizes[:i]):sum(part_sizes[:i + 1])] for i in xrange(len(self.workers))]

        mapped = []

        for i in xrange(0, len(self.workers)):
            #mapped = Solver.mymap(divided_parts[i])
            #output.append(mapped)
            mapped.append(self.workers[i].mymap(divided_parts[i]))

        points = self.myreduce(mapped)

        output = []
        for sublist in points:
            #points.append(sublist)
            for item in sublist:
                output.append(item)

        result = Solver.printHull(output)

        self.write_output(result)

    @staticmethod
    @expose
    def mymap(a):

        return Solver.printHull(a)

    @staticmethod
    @expose
    def myreduce(mapped):

        print("reduce")

        points = []
        for sublist in mapped:
                points.append(sublist.value)
        #for item in sublist:
        #    points.append(item.value)

        #points = [list(item.value).value for sublist in mapped.value for item in sublist.value]

        return points

    @staticmethod
    @expose
    def findSide(p1, p2, p):
        val = (p[1] - p1[1]) * (p2[0] - p1[0]) - (p2[1] - p1[1]) * (p[0] - p1[0])

        if val > 0:
            return 1
        if val < 0:
            return -1
        return 0

    @staticmethod
    @expose
    def lineDist(p1, p2, p):
        return abs((p[1] - p1[1]) * (p2[0] - p1[0]) - (p2[1] - p1[1]) * (p[0] - p1[0]))


    @staticmethod
    @expose
    def quickHull(a, n, p1, p2, side, hull):
        ind = -1
        max_dist = 0

        for i in range(n):
            temp = Solver.lineDist(p1, p2, a[i])

            if (Solver.findSide(p1, p2, a[i]) == side) and (temp > max_dist):
                ind = i
                max_dist = temp

        if ind == -1:
            hull.add("$".join(map(str, p1)))
            hull.add("$".join(map(str, p2)))
            return

        Solver.quickHull(a, n, a[ind], p1, -Solver.findSide(a[ind], p1, p2), hull)
        Solver.quickHull(a, n, a[ind], p2, -Solver.findSide(a[ind], p2, p1), hull)

    @staticmethod
    @expose
    def printHull(a):
        hull = set()
        n = len(a)

        if n < 3:
            print("Convex hull not possible")
            return

        min_x = 0
        max_x = 0
        for i in range(1, n):
            if a[i][0] < a[min_x][0]:
                min_x = i
            if a[i][0] > a[max_x][0]:
                max_x = i

        Solver.quickHull(a, n, a[min_x], a[max_x], 1, hull)
        Solver.quickHull(a, n, a[min_x], a[max_x], -1, hull)

        # print("The points in Convex Hull are:")

        output = []

        for element in hull:
            x = element.split("$")
            output.append(list((int(x[0]), int(x[1]))))

        return output


    def read_input(self):
        points = []
        with open(self.input_file_name, 'r') as f:
            for line in f:
                x, y = map(int, line.split(','))
                points.append([x, y])
        return points

    def write_output(self, output):
        with open(self.output_file_name, 'w') as f:
            #q = 0
            #w = 1 / q
            for list in output:
                #for point in list:
                f.write(str(list[0])+", "+str(list[1])+"\n")
        print("Output done")
