#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Path Planner Module
Cutting Path Optimization using TSP algorithms

Algorithms:
- Nearest Neighbor (quick)
- 2-opt Local Search
- 3-opt Improvement
- Genetic Algorithm TSP
- Simulated Annealing

Uses: qwen3-coder-plus (algorithm optimization)
"""

import math
import random
import time
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional, Callable
from enum import Enum


class PathAlgorithm(Enum):
    """Available path optimization algorithms"""
    NEAREST_NEIGHBOR = "nearest_neighbor"
    TWO_OPT = "2opt"
    THREE_OPT = "3opt"
    GENETIC = "genetic_tsp"
    SIMULATED_ANNEALING = "simulated_annealing"


@dataclass
class CutPoint:
    """A point in the cutting sequence"""
    x: float
    y: float
    part_id: str
    cut_type: str = "perimeter"  # perimeter, edge, hole


@dataclass
class CutSegment:
    """A cutting segment"""
    start_x: float
    start_y: float
    end_x: float
    end_y: float
    part_id: str
    edge_type: str = "linear"  # linear, arc


    @property
    def length(self) -> float:
        return math.sqrt((self.end_x - self.start_x)**2 +
                         (self.end_y - self.start_y)**2)

    @property
    def start_point(self) -> Tuple[float, float]:
        return (self.start_x, self.start_y)

    @property
    def end_point(self) -> Tuple[float, float]:
        return (self.end_x, self.end_y)


class TSPSolver:
    """
    Traveling Salesman Problem solver for cutting path
    Minimizes total travel distance between cuts
    """

    def __init__(self, points: List[Tuple[float, float]],
                 segments: Optional[List[CutSegment]] = None):
        """
        Initialize TSP solver

        Args:
            points: List of (x, y) coordinates to visit
            segments: Optional cutting segments (for segment-based routing)
        """
        self.points = points
        self.n = len(points)
        self.segments = segments

        # Pre-compute distance matrix
        self.dist_matrix = self._compute_distance_matrix()

    def _compute_distance_matrix(self) -> List[List[float]]:
        """Compute pairwise distances"""
        matrix = [[0.0] * self.n for _ in range(self.n)]
        for i in range(self.n):
            for j in range(i + 1, self.n):
                dist = math.sqrt((self.points[i][0] - self.points[j][0])**2 +
                                 (self.points[i][1] - self.points[j][1])**2)
                matrix[i][j] = dist
                matrix[j][i] = dist
        return matrix

    def solve_nearest_neighbor(self, start_idx: int = 0) -> List[int]:
        """
        Nearest neighbor heuristic (fast but not optimal)

        Args:
            start_idx: Starting point index

        Returns:
            Path as list of point indices
        """
        path = [start_idx]
        unvisited = set(range(self.n))
        unvisited.remove(start_idx)

        while unvisited:
            current = path[-1]
            # Find nearest unvisited
            nearest = min(unvisited,
                          key=lambda i: self.dist_matrix[current][i])
            path.append(nearest)
            unvisited.remove(nearest)

        return path

    def solve_2opt(self, initial_path: Optional[List[int]] = None,
                   max_iterations: int = 1000) -> List[int]:
        """
        2-opt local search improvement

        Args:
            initial_path: Starting path (uses NN if None)
            max_iterations: Maximum iterations

        Returns:
            Improved path
        """
        if initial_path is None:
            path = self.solve_nearest_neighbor()
        else:
            path = initial_path[:]

        improved = True
        iterations = 0

        while improved and iterations < max_iterations:
            improved = False
            iterations += 1

            for i in range(1, self.n - 1):
                for j in range(i + 1, self.n):
                    # Calculate improvement
                    current_dist = (self.dist_matrix[path[i-1]][path[i]] +
                                   self.dist_matrix[path[j]][path[(j+1)%self.n]])

                    new_dist = (self.dist_matrix[path[i-1]][path[j]] +
                               self.dist_matrix[path[i]][path[(j+1)%self.n]])

                    if new_dist < current_dist:
                        # Reverse segment
                        path[i:j+1] = path[i:j+1][::-1]
                        improved = True
                        break

                if improved:
                    break

        return path

    def solve_3opt(self, initial_path: Optional[List[int]] = None,
                   max_iterations: int = 500) -> List[int]:
        """
        3-opt local search (better than 2-opt but slower)

        Args:
            initial_path: Starting path
            max_iterations: Maximum iterations

        Returns:
            Improved path
        """
        if initial_path is None:
            path = self.solve_2opt()
        else:
            path = initial_path[:]

        improved = True
        iterations = 0

        while improved and iterations < max_iterations:
            improved = False
            iterations += 1

            for i in range(self.n - 2):
                for j in range(i + 1, self.n - 1):
                    for k in range(j + 1, self.n):
                        # Try all 7 possible 3-opt rearrangements
                        new_path = self._try_3opt_rearrangements(path, i, j, k)
                        if self._path_length(new_path) < self._path_length(path):
                            path = new_path
                            improved = True
                            break

                    if improved:
                        break

                if improved:
                    break

        return path

    def _try_3opt_rearrangements(self, path: List[int],
                                  i: int, j: int, k: int) -> List[int]:
        """Try all 3-opt rearrangements and return best"""
        # 7 possible rearrangements for 3-opt
        arrangements = [
            path[:i] + path[i:j][::-1] + path[j:k][::-1] + path[k:],
            path[:i] + path[i:j][::-1] + path[j:k] + path[k:],
            path[:i] + path[i:j] + path[j:k][::-1] + path[k:],
            path[:i] + path[j:k] + path[i:j] + path[k:],
            path[:i] + path[j:k] + path[i:j][::-1] + path[k:],
            path[:i] + path[i:j][::-1] + path[k:] + path[j:k],
            path[:i] + path[k:] + path[i:j][::-1] + path[j:k],
        ]

        best = min(arrangements, key=lambda p: self._path_length(p))
        return best

    def _path_length(self, path: List[int]) -> float:
        """Calculate total path length"""
        total = 0.0
        for i in range(len(path)):
            total += self.dist_matrix[path[i]][path[(i+1)%self.n]]
        return total

    def solve_genetic(self, population_size: int = 50,
                      generations: int = 100) -> List[int]:
        """
        Genetic algorithm for TSP

        Args:
            population_size: Population size
            generations: Number of generations

        Returns:
            Best path found
        """
        # Initialize population
        population = []
        for _ in range(population_size):
            individual = list(range(self.n))
            random.shuffle(individual)
            population.append(individual)

        best_path = population[0]
        best_length = self._path_length(best_path)

        for gen in range(generations):
            # Evaluate fitness
            fitness = [1.0 / self._path_length(ind) for ind in population]

            # Selection (tournament)
            new_population = []
            while len(new_population) < population_size:
                parent1 = self._tournament_select(population, fitness)
                parent2 = self._tournament_select(population, fitness)

                # Crossover (OX)
                child = self._ox_crossover(parent1, parent2)

                # Mutation (swap)
                if random.random() < 0.1:
                    i, j = random.sample(range(self.n), 2)
                    child[i], child[j] = child[j], child[i]

                new_population.append(child)

            population = new_population

            # Update best
            current_best = min(population, key=lambda p: self._path_length(p))
            current_length = self._path_length(current_best)
            if current_length < best_length:
                best_length = current_length
                best_path = current_best

        return best_path

    def _tournament_select(self, population: List[List[int]],
                          fitness: List[float], k: int = 3) -> List[int]:
        """Tournament selection"""
        tournament = random.sample(list(zip(population, fitness)), k)
        winner = max(tournament, key=lambda x: x[1])
        return winner[0]

    def _ox_crossover(self, parent1: List[int], parent2: List[int]) -> List[int]:
        """Order crossover (OX)"""
        size = len(parent1)
        start, end = sorted(random.sample(range(size), 2))

        child = [None] * size
        child[start:end+1] = parent1[start:end+1]

        # Fill remaining from parent2
        parent2_remaining = [p for p in parent2 if p not in child[start:end+1]]
        idx = 0
        for i in range(size):
            if child[i] is None:
                child[i] = parent2_remaining[idx]
                idx += 1

        return child

    def solve_simulated_annealing(self,
                                  initial_temp: float = 10000,
                                  cooling_rate: float = 0.9995,
                                  min_temp: float = 1) -> List[int]:
        """
        Simulated annealing optimization

        Args:
            initial_temp: Starting temperature
            cooling_rate: Cooling rate per iteration
            min_temp: Minimum temperature

        Returns:
            Best path found
        """
        # Start with NN + 2-opt
        current_path = self.solve_2opt()
        current_length = self._path_length(current_path)

        best_path = current_path[:]
        best_length = current_length

        temp = initial_temp

        while temp > min_temp:
            # Generate neighbor by swapping two cities
            i, j = random.sample(range(self.n), 2)
            new_path = current_path[:]
            new_path[i], new_path[j] = new_path[j], new_path[i]

            new_length = self._path_length(new_path)

            # Accept or reject
            if new_length < current_length:
                current_path = new_path
                current_length = new_length

                if current_length < best_length:
                    best_path = current_path[:]
                    best_length = current_length
            else:
                # Accept with probability exp(-delta/T)
                delta = new_length - current_length
                if random.random() < math.exp(-delta / temp):
                    current_path = new_path
                    current_length = new_length

            # Cool down
            temp *= cooling_rate

        return best_path


class CuttingPathOptimizer:
    """
    Main path optimizer for glass cutting
    Handles both point-based and segment-based routing
    """

    def __init__(self, sheet_width: float = 6000, sheet_height: float = 3000):
        """
        Initialize path optimizer

        Args:
            sheet_width: Sheet width (mm)
            sheet_height: Sheet height (mm)
        """
        self.sheet_width = sheet_width
        self.sheet_height = sheet_height
        self.start_point = (0, 0)  # Home position

    def optimize(self,
                 placed_parts: List[Dict],
                 algorithm: PathAlgorithm = PathAlgorithm.TWO_OPT,
                 consider_segments: bool = True) -> Dict:
        """
        Optimize cutting path

        Args:
            placed_parts: List of placed parts with positions
            algorithm: Algorithm to use
            consider_segments: Whether to consider segment routing

        Returns:
            Optimization result
        """
        # Generate cut points/segments from placed parts
        if consider_segments:
            segments = self._generate_segments(placed_parts)
            # Use only part centers for TSP, not all segment points
            points = self._generate_points(placed_parts)
            segments = None  # We'll use points instead
        else:
            points = self._generate_points(placed_parts)
            segments = None

        # Create TSP solver
        solver = TSPSolver(points, segments)

        # Solve based on algorithm
        start_time = time.time()

        if algorithm == PathAlgorithm.NEAREST_NEIGHBOR:
            path = solver.solve_nearest_neighbor()
        elif algorithm == PathAlgorithm.TWO_OPT:
            path = solver.solve_2opt()
        elif algorithm == PathAlgorithm.THREE_OPT:
            path = solver.solve_3opt()
        elif algorithm == PathAlgorithm.GENETIC:
            path = solver.solve_genetic()
        elif algorithm == PathAlgorithm.SIMULATED_ANNEALING:
            path = solver.solve_simulated_annealing()
        else:
            path = solver.solve_2opt()

        elapsed = time.time() - start_time

        # Calculate metrics
        total_distance = solver._path_length(path)
        # Calculate cut distance from placed parts
        cut_distance = sum(2 * (p.get("placed_width", p.get("width", 100)) +
                                p.get("placed_height", p.get("height", 100)))
                           for p in placed_parts)

        return {
            "path": path,
            "total_travel_distance": total_distance,
            "cut_distance": cut_distance,
            "total_distance": total_distance + cut_distance,
            "optimization_time": elapsed,
            "algorithm": algorithm.value,
            "ordered_parts": [placed_parts[i] for i in path if i < len(placed_parts)]
        }

    def _generate_points(self, placed_parts: List[Dict]) -> List[Tuple[float, float]]:
        """Generate cut points from placed parts"""
        points = []
        for part in placed_parts:
            # Use part center as cut point
            center_x = part["x"] + part.get("placed_width", part["width"]) / 2
            center_y = part["y"] + part.get("placed_height", part["height"]) / 2
            points.append((center_x, center_y))
        return points

    def _generate_segments(self, placed_parts: List[Dict]) -> List[CutSegment]:
        """Generate cutting segments from placed parts"""
        segments = []

        for part in placed_parts:
            x = part["x"]
            y = part["y"]
            w = part.get("placed_width", part["width"])
            h = part.get("placed_height", part["height"])
            part_id = part.get("order_id", part.get("part_id", "unknown"))

            # Perimeter cuts (rectangle)
            # Bottom edge
            segments.append(CutSegment(x, y, x + w, y, part_id, "linear"))
            # Right edge
            segments.append(CutSegment(x + w, y, x + w, y + h, part_id, "linear"))
            # Top edge
            segments.append(CutSegment(x + w, y + h, x, y + h, part_id, "linear"))
            # Left edge
            segments.append(CutSegment(x, y + h, x, y, part_id, "linear"))

        return segments

    def optimize_multi_algorithm(self, placed_parts: List[Dict]) -> Dict:
        """
        Try multiple algorithms and return best result

        Args:
            placed_parts: List of placed parts

        Returns:
            Best optimization result
        """
        results = []

        for algo in [PathAlgorithm.TWO_OPT, PathAlgorithm.THREE_OPT,
                     PathAlgorithm.SIMULATED_ANNEALING]:
            result = self.optimize(placed_parts, algo)
            results.append(result)

        # Return shortest path
        best = min(results, key=lambda r: r["total_travel_distance"])
        return best


def demo():
    """Demo usage"""
    print("=" * 60)
    print("Path Planner Demo")
    print("=" * 60)

    # Sample placed parts
    placed_parts = [
        {"x": 0, "y": 0, "width": 500, "height": 400, "order_id": "P1"},
        {"x": 500, "y": 0, "width": 300, "height": 200, "order_id": "P2"},
        {"x": 0, "y": 400, "width": 800, "height": 600, "order_id": "P3"},
        {"x": 800, "y": 0, "width": 400, "height": 300, "order_id": "P4"},
    ]

    # Create optimizer
    optimizer = CuttingPathOptimizer(6000, 3000)

    # Run optimization
    result = optimizer.optimize(placed_parts, PathAlgorithm.TWO_OPT)

    print(f"\nAlgorithm: {result['algorithm']}")
    print(f"Travel distance: {result['total_travel_distance']:.0f} mm")
    print(f"Cut distance: {result['cut_distance']:.0f} mm")
    print(f"Total distance: {result['total_distance']:.0f} mm")
    print(f"Time: {result['optimization_time']:.3f}s")

    print("\nCutting sequence:")
    for i, part in enumerate(result['ordered_parts']):
        print(f"  {i+1}. {part['order_id']} at ({part['x']}, {part['y']})")

    # Multi-algorithm comparison
    print("\n--- Multi-algorithm comparison ---")
    best = optimizer.optimize_multi_algorithm(placed_parts)
    print(f"Best algorithm: {best['algorithm']}")
    print(f"Best distance: {best['total_travel_distance']:.0f} mm")


if __name__ == "__main__":
    demo()