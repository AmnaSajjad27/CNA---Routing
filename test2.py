#!/usr/bin/env python3
import sys

class Router:
    def __init__(self, name):
        self.name = name
        self.neighbors = {}
        self.link_state_database = {}
        self.routing_table = {}

    def update_neighbor(self, neighbor, cost):
        if cost == -1:
            if neighbor in self.neighbors:
                del self.neighbors[neighbor]
        else:
            self.neighbors[neighbor] = cost

    def print_neighbor_table(self):
        print(f"{self.name} Neighbour Table:")
        for neighbor, cost in sorted(self.neighbors.items()):
            print(f"{neighbor}|{cost}")
        print()

    def update_link_state_database(self, router_1, router_2, cost):
        key = (router_1, router_2) if router_1 < router_2 else (router_2, router_1)
        if cost == -1:
            if key in self.link_state_database:
                del self.link_state_database[key]
        else:
            self.link_state_database[key] = cost

    def print_link_state_database(self):
        print(f"{self.name} LSDB:")
        for (router_1, router_2), cost in sorted(self.link_state_database.items()):
            print(f"{router_1}|{router_2}|{cost}")
        print()

    def compute_routing_table(self, graph):
        not_visited = {router: float('inf') for router in graph}
        not_visited[self.name] = 0
        visited = {}
        path = {}

        while not_visited:
            min_router_cost = min(not_visited, key=not_visited.get)
            min_distance = not_visited[min_router_cost]

            for neighbor, cost in graph[min_router_cost].items():
                if neighbor not in not_visited:
                    continue
                new_distance = min_distance + cost
                if new_distance < not_visited[neighbor]:
                    not_visited[neighbor] = new_distance
                    path[neighbor] = min_router_cost

            visited[min_router_cost] = not_visited[min_router_cost]
            not_visited.pop(min_router_cost)

        self.routing_table = {}
        for dest in visited:
            if dest == self.name:
                continue
            next_hop = dest
            while path.get(next_hop) != self.name and path.get(next_hop):
                next_hop = path[next_hop]
            self.routing_table[dest] = (next_hop, visited[dest])

    def print_routing_table(self):
        print(f"{self.name} Routing Table:")
        for dest in sorted(self.routing_table):
            next_hop, cost = self.routing_table[dest]
            print(f"{dest}|{next_hop}|{cost}")
        print()


def main():
    input_data = sys.stdin.read().splitlines()

    routers = {}
    state = None
    update_list = []
    temp_routers_to_print = []

    def update_graph():
        graph = {router_name: router.neighbors.copy() for router_name, router in routers.items()}
        for router in routers.values():
            router.compute_routing_table(graph)

    def process_router_update(routers_to_print):
        for router_name in routers_to_print:
            if router_name in routers:
                router = routers[router_name]
                router.print_neighbor_table()
                router.print_link_state_database()
                router.print_routing_table()
            else:
                # Print empty tables for non-existent routers
                print(f"{router_name} Neighbour Table:\n")
                print(f"{router_name} LSDB:\n")
                print(f"{router_name} Routing Table:\n")

    for line in input_data:
        if line in ["LINKSTATE", "UPDATE", "END"]:
            if state == "END":
                update_graph()
                process_router_update(temp_routers_to_print)
                temp_routers_to_print = []
            state = line
            if state == "UPDATE":
                update_graph()
                for router_name in update_list:
                    if router_name not in routers:
                        routers[router_name] = Router(router_name)
                process_router_update(update_list)
                update_list = []
            continue

        if state in ["LINKSTATE", "UPDATE"]:
            parts = line.split()
            if len(parts) == 1:
                update_list.append(parts[0])
                continue

            link = parts[0].split('-')
            router_1, router_2 = link
            cost = int(parts[1])

            if router_1 not in routers:
                routers[router_1] = Router(router_1)
            if router_2 not in routers:
                routers[router_2] = Router(router_2)

            # Update neighbors and LSDB for both routers involved in the link
            routers[router_1].update_neighbor(router_2, cost)
            routers[router_2].update_neighbor(router_1, cost)
            routers[router_1].update_link_state_database(router_1, router_2, cost)
            routers[router_2].update_link_state_database(router_1, router_2, cost)

            # Propagate LSDB update to all routers
            for r in routers.values():
                r.link_state_database = routers[router_1].link_state_database.copy()

            if len(parts) == 3:
                optional_list = parts[2].split(',')
                update_graph()
                process_router_update(optional_list)

    if state == "END":
        update_graph()
        process_router_update(temp_routers_to_print)

if __name__ == "__main__":
    main()
