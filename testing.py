import lhe_reader

reader = lhe_reader.lhe_reader('test/testing_portions.lhe')

processed_events = reader.processed_events

testing = processed_events[0].root

# for particle in testing.parents:
#     print(particle)
#     print(particle.is_production_particle, particle.is_final_state_particle)
    # print(particle.parents)

# print()


# for item in processed_events[0]:
    # item.print()

processed_events[0].print()

# print(processed_events[0:2])

# print(processed_events[0].root.children)