
def main(seeds, positions):
    
    seed = []
    for ii in range(len(positions)):
        seed.append(seeds[positions[ii]])
    print("".join(seed))

    for i in range(len(positions)):
        if i < len(seeds):
            positions[i] = positions[i] + 1
            if positions[i] < len(seeds):
                return main(seeds, positions)
            positions[i] = 0
        else:
            positions[i] = 0
        
seeds = list("abcd")
main(seeds, [0,0])
