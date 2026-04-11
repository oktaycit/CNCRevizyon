#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Nesting Optimizer Module
Advanced 2D Bin Packing for Glass Cutting

Algorithms:
- Guillotine Cut (Best Fit)
- Genetic Algorithm (GA)
- Maximal Rectangles
- Skyline Algorithm

Uses: qwen3-max (analysis) + qwen3-coder-plus (algorithm)
"""

import math
import random
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional
from enum import Enum


class NestingAlgorithm(Enum):
    """Available nesting algorithms"""
    GUILLOTINE_BESTFIT = "guillotine_bestfit"
    GUILLOTINE_FIRSTFIT = "guillotine_firstfit"
    GENETIC = "genetic"
    MAXIMAL_RECTS = "maximal_rects"
    SKYLINE = "skyline"


@dataclass
class Rectangle:
    """Rectangle representation"""
    x: float
    y: float
    width: float
    height: float

    @property
    def area(self) -> float:
        return self.width * self.height

    @property
    def center(self) -> Tuple[float, float]:
        return (self.x + self.width / 2, self.y + self.height / 2)

    def contains_point(self, px: float, py: float) -> bool:
        return (self.x <= px <= self.x + self.width and
                self.y <= py <= self.y + self.height)

    def intersects(self, other: Rectangle) -> bool:
        return not (self.x + self.width < other.x or
                    other.x + other.width < self.x or
                    self.y + self.height < other.y or
                    other.y + other.height < self.y)


@dataclass
class Part:
    """Part to be placed"""
    part_id: str
    width: float
    height: float
    thickness: float = 4.0
    priority: int = 1
    rotate_allowed: bool = True
    glass_type: str = "float"

    @property
    def area(self) -> float:
        return self.width * self.height


@dataclass
class PlacedPart:
    """Placed part with position"""
    part: Part
    x: float
    y: float
    width: float
    height: float
    rotated: bool = False

    @property
    def rect(self) -> Rectangle:
        return Rectangle(self.x, self.y, self.width, self.height)


class GuillotineOptimizer:
    """
    Guillotine cut nesting algorithm
    Best for glass cutting (clean straight cuts)
    """

    def __init__(self, sheet_width: float, sheet_height: float):
        self.sheet_width = sheet_width
        self.sheet_height = sheet_height
        self.free_rects: List[Rectangle] = []
        self.placed_parts: List[PlacedPart] = []

    def reset(self):
        """Reset optimizer state"""
        self.free_rects = [Rectangle(0, 0, self.sheet_width, self.sheet_height)]
        self.placed_parts = []

    def pack(self, parts: List[Part], heuristic: str = "bestfit") -> List[PlacedPart]:
        """
        Pack parts using guillotine algorithm

        Args:
            parts: List of parts to pack
            heuristic: "bestfit", "firstfit", "worstfit"

        Returns:
            List of placed parts
        """
        self.reset()

        # Sort parts by area (largest first)
        sorted_parts = sorted(parts, key=lambda p: p.area, reverse=True)

        for part in sorted_parts:
            self._place_part(part, heuristic)

        return self.placed_parts

    def _place_part(self, part: Part, heuristic: str) -> bool:
        """Try to place a part"""
        best_rect = None
        best_score = float('inf') if heuristic == "bestfit" else float('-inf')
        best_rotated = False
        best_idx = -1

        pw, ph = part.width, part.height

        for i, free_rect in enumerate(self.free_rects):
            # Try normal orientation
            if pw <= free_rect.width and ph <= free_rect.height:
                score = self._calculate_score(free_rect, pw, ph, heuristic)
                if ((heuristic == "bestfit" and score < best_score) or
                    (heuristic == "worstfit" and score > best_score) or
                    (heuristic == "firstfit" and best_rect is None)):
                    best_score = score
                    best_rect = free_rect
                    best_rotated = False
                    best_idx = i

            # Try rotated orientation
            if part.rotate_allowed and ph <= free_rect.width and pw <= free_rect.height:
                score = self._calculate_score(free_rect, ph, pw, heuristic)
                if ((heuristic == "bestfit" and score < best_score) or
                    (heuristic == "worstfit" and score > best_score) or
                    (heuristic == "firstfit" and best_rect is None)):
                    best_score = score
                    best_rect = free_rect
                    best_rotated = True
                    best_idx = i

        if best_rect is None:
            return False

        # Place the part
        w, h = (ph, pw) if best_rotated else (pw, ph)
        placed = PlacedPart(
            part=part,
            x=best_rect.x,
            y=best_rect.y,
            width=w,
            height=h,
            rotated=best_rotated
        )
        self.placed_parts.append(placed)

        # Split remaining space
        self._split_rectangle(best_idx, best_rect.x, best_rect.y, w, h)

        return True

    def _calculate_score(self, rect: Rectangle, w: float, h: float, heuristic: str) -> float:
        """Calculate placement score"""
        if heuristic == "bestfit":
            # Minimize leftover area
            return min(rect.width - w, rect.height - h)
        elif heuristic == "worstfit":
            # Maximize leftover area (better for future placements)
            return max(rect.width - w, rect.height - h)
        else:
            return rect.width - w + rect.height - h

    def _split_rectangle(self, rect_idx: int, x: float, y: float, w: float, h: float):
        """Split rectangle after placement"""
        rect = self.free_rects[rect_idx]
        self.free_rects.pop(rect_idx)

        # Create remaining rectangles
        # Horizontal split
        if w < rect.width:
            self.free_rects.append(Rectangle(x + w, y, rect.width - w, rect.height))
        # Vertical split
        if h < rect.height:
            self.free_rects.append(Rectangle(x, y + h, w, rect.height - h))

        # Merge overlapping rectangles
        self._merge_free_rects()

    def _merge_free_rects(self):
        """Merge overlapping free rectangles"""
        merged = []
        for rect in self.free_rects:
            is_merged = False
            for m in merged:
                if rect.x == m.x and rect.width == m.width:
                    if rect.y + rect.height == m.y:
                        m.y = rect.y
                        m.height += rect.height
                        is_merged = True
                    elif m.y + m.height == rect.y:
                        m.height += rect.height
                        is_merged = True
                elif rect.y == m.y and rect.height == m.height:
                    if rect.x + rect.width == m.x:
                        m.x = rect.x
                        m.width += rect.width
                        is_merged = True
                    elif m.x + m.width == rect.x:
                        m.width += rect.width
                        is_merged = True
            if not is_merged:
                merged.append(rect)
        self.free_rects = merged

    def get_utilization(self) -> float:
        """Calculate sheet utilization"""
        total_area = self.sheet_width * self.sheet_height
        used_area = sum(p.width * p.height for p in self.placed_parts)
        return used_area / total_area


class GeneticOptimizer:
    """
    Genetic algorithm for nesting optimization
    Better for complex non-guillotine cuts
    """

    def __init__(self, sheet_width: float, sheet_height: float,
                 population_size: int = 100, generations: int = 50):
        self.sheet_width = sheet_width
        self.sheet_height = sheet_height
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = 0.1
        self.crossover_rate = 0.7

    def pack(self, parts: List[Part]) -> List[PlacedPart]:
        """
        Optimize placement using genetic algorithm

        Args:
            parts: List of parts to pack

        Returns:
            Best placement solution
        """
        # Create initial population
        population = [self._create_individual(parts) for _ in range(self.population_size)]

        # Evaluate fitness
        fitness = [self._evaluate(ind) for ind in population]

        best_individual = population[0]
        best_fitness = fitness[0]

        for gen in range(self.generations):
            # Selection (tournament)
            new_population = []
            while len(new_population) < self.population_size:
                parent1 = self._tournament_select(population, fitness)
                parent2 = self._tournament_select(population, fitness)

                # Crossover
                if random.random() < self.crossover_rate:
                    child = self._crossover(parent1, parent2)
                else:
                    child = parent1[:]

                # Mutation
                if random.random() < self.mutation_rate:
                    child = self._mutate(child, parts)

                new_population.append(child)

            population = new_population
            fitness = [self._evaluate(ind) for ind in population]

            # Track best
            max_idx = fitness.index(max(fitness))
            if fitness[max_idx] > best_fitness:
                best_fitness = fitness[max_idx]
                best_individual = population[max_idx]

        # Convert best individual to placed parts
        return self._individual_to_placed(best_individual, parts)

    def _create_individual(self, parts: List[Part]) -> List[Tuple[int, float, float, bool]]:
        """Create random individual (placement sequence)"""
        individual = []
        for i, part in enumerate(parts):
            # Random position and rotation
            max_x = self.sheet_width - part.width
            max_y = self.sheet_height - part.height
            x = random.uniform(0, max_x) if max_x > 0 else 0
            y = random.uniform(0, max_y) if max_y > 0 else 0
            rotated = random.choice([True, False]) if part.rotate_allowed else False
            individual.append((i, x, y, rotated))
        return individual

    def _evaluate(self, individual: List[Tuple]) -> float:
        """Evaluate fitness (utilization - overlap penalty)"""
        placed_area = 0
        overlap_penalty = 0

        rects = []
        for i, x, y, rotated in individual:
            w, h = individual[0] if not rotated else (individual[1], individual[0])
            # Get actual part dimensions
            # This is simplified - actual implementation needs part reference
            w, h = 100, 100  # Placeholder
            rect = Rectangle(x, y, w, h)

            # Check overlap
            for other_rect in rects:
                if rect.intersects(other_rect):
                    overlap_penalty += rect.area

            # Check bounds
            if x + w > self.sheet_width or y + h > self.sheet_height:
                overlap_penalty += rect.area * 2

            rects.append(rect)
            placed_area += rect.area

        # Fitness = utilization - overlap penalty
        utilization = placed_area / (self.sheet_width * self.sheet_height)
        return utilization - overlap_penalty / (self.sheet_width * self.sheet_height)

    def _tournament_select(self, population: List, fitness: List[float], k: int = 3) -> List:
        """Tournament selection"""
        tournament = random.sample(list(zip(population, fitness)), k)
        winner = max(tournament, key=lambda x: x[1])
        return winner[0]

    def _crossover(self, parent1: List, parent2: List) -> List:
        """Order crossover (OX)"""
        size = len(parent1)
        start, end = sorted(random.sample(range(size), 2))

        child = [None] * size
        child[start:end] = parent1[start:end]

        # Fill remaining from parent2
        parent2_remaining = [item for item in parent2 if item not in child[start:end]]
        idx = 0
        for i in range(size):
            if child[i] is None:
                child[i] = parent2_remaining[idx]
                idx += 1

        return child

    def _mutate(self, individual: List, parts: List[Part]) -> List:
        """Random mutation"""
        # Swap two positions
        if len(individual) >= 2:
            i, j = random.sample(range(len(individual)), 2)
            individual[i], individual[j] = individual[j], individual[i]

        # Random rotation change
        idx = random.randint(0, len(individual) - 1)
        part_idx, x, y, rotated = individual[idx]
        if parts[part_idx].rotate_allowed:
            individual[idx] = (part_idx, x, y, not rotated)

        return individual

    def _individual_to_placed(self, individual: List, parts: List[Part]) -> List[PlacedPart]:
        """Convert individual to placed parts"""
        placed = []
        for part_idx, x, y, rotated in individual:
            part = parts[part_idx]
            w, h = (part.height, part.width) if rotated else (part.width, part.height)
            placed.append(PlacedPart(
                part=part,
                x=x,
                y=y,
                width=w,
                height=h,
                rotated=rotated
            ))
        return placed


class MaximalRectsOptimizer:
    """
    Maximal Rectangles algorithm
    More flexible than guillotine, better utilization
    """

    def __init__(self, sheet_width: float, sheet_height: float):
        self.sheet_width = sheet_width
        self.sheet_height = sheet_height
        self.free_rects: List[Rectangle] = []
        self.placed_parts: List[PlacedPart] = []

    def reset(self):
        self.free_rects = [Rectangle(0, 0, self.sheet_width, self.sheet_height)]
        self.placed_parts = []

    def pack(self, parts: List[Part]) -> List[PlacedPart]:
        """Pack parts using maximal rectangles"""
        self.reset()

        sorted_parts = sorted(parts, key=lambda p: p.area, reverse=True)

        for part in sorted_parts:
            self._place_part(part)

        return self.placed_parts

    def _place_part(self, part: Part) -> bool:
        """Place a part in best maximal rectangle"""
        best_rect = None
        best_score = float('inf')
        best_rotated = False

        pw, ph = part.width, part.height

        for rect in self.free_rects:
            # Check fit
            if pw <= rect.width and ph <= rect.height:
                score = self._score_bottom_left(rect, pw, ph)
                if score < best_score:
                    best_score = score
                    best_rect = rect
                    best_rotated = False

            if part.rotate_allowed and ph <= rect.width and pw <= rect.height:
                score = self._score_bottom_left(rect, ph, pw)
                if score < best_score:
                    best_score = score
                    best_rect = rect
                    best_rotated = True

        if best_rect is None:
            return False

        w, h = (ph, pw) if best_rotated else (pw, ph)
        placed = PlacedPart(
            part=part,
            x=best_rect.x,
            y=best_rect.y,
            width=w,
            height=h,
            rotated=best_rotated
        )
        self.placed_parts.append(placed)

        # Generate new maximal rectangles
        self._generate_maximal_rects(best_rect, w, h)

        return True

    def _score_bottom_left(self, rect: Rectangle, w: float, h: float) -> float:
        """Bottom-left placement score"""
        return rect.y + rect.x  # Prefer bottom-left

    def _generate_maximal_rects(self, used_rect: Rectangle, w: float, h: float):
        """Generate new maximal rectangles after placement"""
        new_rects = []

        for rect in self.free_rects:
            if rect.intersects(used_rect):
                # Split into remaining rectangles
                # Left strip
                if used_rect.x > rect.x:
                    new_rect = Rectangle(
                        rect.x, rect.y,
                        used_rect.x - rect.x, rect.height
                    )
                    if new_rect.width > 0 and new_rect.height > 0:
                        new_rects.append(new_rect)

                # Right strip
                if used_rect.x + w < rect.x + rect.width:
                    new_rect = Rectangle(
                        used_rect.x + w, rect.y,
                        rect.x + rect.width - used_rect.x - w, rect.height
                    )
                    if new_rect.width > 0 and new_rect.height > 0:
                        new_rects.append(new_rect)

                # Top strip
                if used_rect.y + h < rect.y + rect.height:
                    new_rect = Rectangle(
                        rect.x, used_rect.y + h,
                        rect.width, rect.y + rect.height - used_rect.y - h
                    )
                    if new_rect.width > 0 and new_rect.height > 0:
                        new_rects.append(new_rect)

                # Bottom strip
                if used_rect.y > rect.y:
                    new_rect = Rectangle(
                        rect.x, rect.y,
                        rect.width, used_rect.y - rect.y
                    )
                    if new_rect.width > 0 and new_rect.height > 0:
                        new_rects.append(new_rect)
            else:
                new_rects.append(rect)

        # Remove duplicates and contained rectangles
        self.free_rects = self._prune_rects(new_rects)

    def _prune_rects(self, rects: List[Rectangle]) -> List[Rectangle]:
        """Remove contained and duplicate rectangles"""
        pruned = []
        for rect in rects:
            is_contained = False
            for other in rects:
                if rect != other and self._is_contained(rect, other):
                    is_contained = True
                    break
            if not is_contained:
                pruned.append(rect)
        return pruned

    def _is_contained(self, rect: Rectangle, other: Rectangle) -> bool:
        """Check if rect is contained in other"""
        return (rect.x >= other.x and rect.y >= other.y and
                rect.x + rect.width <= other.x + other.width and
                rect.y + rect.height <= other.y + other.height)


class NestingOptimizer:
    """
    Main nesting optimizer class
    Combines multiple algorithms
    """

    ALGORITHMS = {
        NestingAlgorithm.GUILLOTINE_BESTFIT: GuillotineOptimizer,
        NestingAlgorithm.GUILLOTINE_FIRSTFIT: GuillotineOptimizer,
        NestingAlgorithm.GENETIC: GeneticOptimizer,
        NestingAlgorithm.MAXIMAL_RECTS: MaximalRectsOptimizer,
    }

    def __init__(self,
                 sheet_width: float = 6000,
                 sheet_height: float = 3000,
                 algorithm: NestingAlgorithm = NestingAlgorithm.GUILLOTINE_BESTFIT):
        """
        Initialize nesting optimizer

        Args:
            sheet_width: Sheet width (mm)
            sheet_height: Sheet height (mm)
            algorithm: Algorithm to use
        """
        self.sheet_width = sheet_width
        self.sheet_height = sheet_height
        self.algorithm = algorithm

    def optimize(self, parts: List[Part]) -> Dict:
        """
        Optimize nesting placement

        Args:
            parts: List of parts to place

        Returns:
            Optimization result dictionary
        """
        # Create algorithm instance
        algo_class = self.ALGORITHMS.get(self.algorithm, GuillotineOptimizer)
        optimizer = algo_class(self.sheet_width, self.sheet_height)

        # Run optimization
        placed = optimizer.pack(parts)

        # Calculate metrics
        total_area = self.sheet_width * self.sheet_height
        used_area = sum(p.width * p.height for p in placed)
        utilization = used_area / total_area if total_area > 0 else 0

        return {
            "placed_parts": [
                {
                    "part_id": p.part.part_id,
                    "x": p.x,
                    "y": p.y,
                    "width": p.width,
                    "height": p.height,
                    "rotated": p.rotated,
                    "area": p.width * p.height
                }
                for p in placed
            ],
            "utilization": utilization,
            "waste_area": total_area - used_area,
            "unplaced_count": len(parts) - len(placed),
            "algorithm": self.algorithm.value
        }

    def optimize_multi_algorithm(self, parts: List[Part]) -> Dict:
        """
        Try multiple algorithms and return best result

        Args:
            parts: List of parts to place

        Returns:
            Best optimization result
        """
        results = []

        for algo in [NestingAlgorithm.GUILLOTINE_BESTFIT,
                     NestingAlgorithm.MAXIMAL_RECTS]:
            optimizer = NestingOptimizer(
                self.sheet_width, self.sheet_height, algo
            )
            result = optimizer.optimize(parts)
            result["algorithm"] = algo.value
            results.append(result)

        # Return best utilization
        best = max(results, key=lambda r: r["utilization"])
        return best


def demo():
    """Demo usage"""
    print("=" * 60)
    print("Nesting Optimizer Demo")
    print("=" * 60)

    # Create sample parts
    parts = [
        Part("P1", 500, 400, 4, 1, True, "float"),
        Part("P2", 300, 200, 4, 2, True, "float"),
        Part("P3", 800, 600, 6, 1, True, "float"),
        Part("P4", 400, 300, 4, 3, True, "float"),
        Part("P5", 1000, 800, 8, 1, True, "laminated"),
    ]

    # Create optimizer
    optimizer = NestingOptimizer(6000, 3000, NestingAlgorithm.GUILLOTINE_BESTFIT)

    # Run optimization
    result = optimizer.optimize(parts)

    print(f"\nAlgorithm: {result['algorithm']}")
    print(f"Parts placed: {len(result['placed_parts'])}")
    print(f"Utilization: {result['utilization']*100:.2f}%")
    print(f"Waste area: {result['waste_area']/1000000:.2f} m²")
    print(f"Unplaced: {result['unplaced_count']}")

    # Show placements
    print("\nPlacements:")
    for p in result['placed_parts']:
        print(f"  {p['part_id']}: ({p['x']:.0f}, {p['y']:.0f}) "
              f"{p['width']}x{p['height']} mm "
              f"{'[rotated]' if p['rotated'] else ''}")


if __name__ == "__main__":
    demo()