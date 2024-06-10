import math
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

        width, height, seeds = self.read_input()

        regions = []
        step = height // len(self.workers)

        for i in xrange(len(self.workers)):
            y1 = i * step
            y2 = (i + 1) * step - 1 if i != len(self.workers) - 1 else height - 1
            regions.append((0, y1, width - 1, y2))

        mapped = []

        for i in xrange(len(self.workers)):
            result = self.workers[i].mymap(regions[i][0], regions[i][1], regions[i][2], regions[i][3], seeds)
            mapped.append(result)

        final_results = self.myreduce(mapped)

        self.write_output(final_results, width, height)

    @staticmethod
    @expose
    def mymap(x1, y1, x2, y2, seeds):
        result = []
        return Solver.process_rectangle(x1, y1, x2, y2, seeds, result)

    @staticmethod
    @expose
    def myreduce(mapped):
        print("reduce")

        result = []
        for sublist in mapped:
            result.extend(sublist.value)

        return result

    @staticmethod
    @expose
    def euclidean_distance(p1, p2):
        return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)

    @staticmethod
    @expose
    def closest_seed(point, seeds):
        min_distance = float('inf')
        closest = None
        for seed in seeds:
            distance = Solver.euclidean_distance(point, seed)
            if distance < min_distance:
                min_distance = distance
                closest = seed
        return closest

    @staticmethod
    @expose
    def process_rectangle(x1, y1, x2, y2, seeds, result):
        # Base case: if the rectangle is a single point
        if x1 == x2 and y1 == y2:
            result.append(((x1, y1), Solver.closest_seed((x1, y1), seeds)))
            return result

        # Calculate the corner points
        corners = [(x1, y1), (x2, y1), (x1, y2), (x2, y2)]

        # Find the closest seeds to each corner point
        closest_seeds = [Solver.closest_seed(corner, seeds) for corner in corners]

        # Check if all corner points are closest to the same seed
        if all(seed == closest_seeds[0] for seed in closest_seeds):
            seed = closest_seeds[0]
            for i in xrange(x1, x2 + 1):
                for j in xrange(y1, y2 + 1):
                    result.append(((i, j), seed))
        else:
            # Subdivide the rectangle into four smaller rectangles and process each
            mid_x = (x1 + x2) // 2
            mid_y = (y1 + y2) // 2

            if x1 <= mid_x and y1 <= mid_y:
                Solver.process_rectangle(x1, y1, mid_x, mid_y, seeds, result)
            if mid_x + 1 <= x2 and y1 <= mid_y:
                Solver.process_rectangle(mid_x + 1, y1, x2, mid_y, seeds, result)
            if x1 <= mid_x and mid_y + 1 <= y2:
                Solver.process_rectangle(x1, mid_y + 1, mid_x, y2, seeds, result)
            if mid_x + 1 <= x2 and mid_y + 1 <= y2:
                Solver.process_rectangle(mid_x + 1, mid_y + 1, x2, y2, seeds, result)

        return result

    def read_input(self):
        with open(self.input_file_name, 'r') as f:
            lines = f.readlines()
            width, height = map(int, lines[0].split())
            seeds = [tuple(map(int, line.split())) for line in lines[1:]]
        return width, height, seeds

    def write_output(self, result, width, height):
        with open(self.output_file_name, 'w') as f:
            grid = [[''] * width for _ in xrange(height)]
            for (x, y), seed in result:
                grid[y][x] = seed
            for row in grid:
                f.write(' '.join(map(str, row)) + '\n')
        print("Output done")


