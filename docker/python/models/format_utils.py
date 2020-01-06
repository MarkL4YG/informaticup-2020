
def strength_to_int(stren) -> int:
    if "+" in stren:
        return len(stren)
    elif "o" == stren:
        return 0
    else:
        return -len(stren)
