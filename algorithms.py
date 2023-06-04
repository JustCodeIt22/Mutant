# Convert to Percentage
def cnv_to_per(percent, of=100):
    result = percent/100 * of
    return result

# Search all occurences of Substring in a string using (Z algorithm)
def create_Zarr(string, z):
    size = len(string)
    left, right, k = 0, 0, 0
    for i in range(1, size):
        if i > right:
            left, right = i, i
            while right < size and string[right - left] == string[right]:
                right += 1
            z[i] = right - left # add the index
            right -= 1
        else:
            k = i - left
            if z[k] < right - i + 1:
                z[i] = z[k]
            else:
                left = i
                while right < size and string[right - left] == string[right]:
                    right += 1
                z[i] = right - left
                right -= 1
            

def findString(string, substr):
    idxs = []
    concat = substr + "$" + string
    left = len(concat)

    #Construct Z array
    z = [0] * left  # creating array of 0 of size left
    create_Zarr(concat, z)

    for i in range(left):
        if z[i] == len(substr):
            idxs.append(i - len(substr) - 1)
    
    return idxs