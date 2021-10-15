import numpy

def running_average(data, winsize):

    # running average
    # If the neighborhood around a point includes a point outside the array, 
    # a "mirrored" edge point is used to compute the smoothed result

    array = numpy.array(data)
    N = len(array)
    smoothed_array = numpy.zeros(N) # init smoothed array 

    for i in range(N):

        # basically, the following formula is implemented (in tex):
        # a[i] = 1/winsize \sum_{j=0}^{j=winsize-1} a[i-winsize/2+j]

        inds = numpy.array(range(winsize))

        for j in range(winsize):
            if (i-winsize/2+j) > (N-1):
                inds[j]=int((N-1)-((i-winsize/2+j)%(N-1)))
            else:
                inds[j]=int(abs(i - winsize/2 + j))

        smoothed_array[i] = numpy.mean(array[inds])

    return smoothed_array

