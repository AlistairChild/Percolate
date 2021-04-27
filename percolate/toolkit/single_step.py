"""Copyright (c) 2021 Alistair Child

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE."""
import numpy as np
import array

from percolate.toolkit.find_array_equivalent import find_array_equivalent
from percolate.toolkit.zerolistmaker import zerolistmaker
from scipy.special import comb

"""def smoothstep(x, x_min=0, x_max=1, N=3):
	x = np.clip((x - x_min) / (x_max - x_min), 0, 1)
	result=0
	for n in range(0, N+1):
		result += comb(N + n, n) * comb(2 * N + 1, N - n) * (-x) ** n
	
	result *= x ** (N + 1)
	return result

def single_step(energy, absorption, args):
	
	loc_energy = energy
	loc_absorption = absorption

	if len(np.array(loc_absorption).shape) > 1:
		n_files = len(np.array(loc_absorption))
	else:
		n_files = 1
		
	step = []
	subtracted_step = []
	
	for i in range(n_files):
	    
		if args.apply_step == "on":
			#dummy variables
						
			#find array point
			step_stop_energy = find_array_equivalent(loc_energy[i], args.step_stop)
			step_start_energy = find_array_equivalent(loc_energy[i], args.step_start)	
			edge = find_array_equivalent(loc_energy[i], args.edge)	

			
			el3_cut = step_start_energy - step_stop_energy
			


			#create a linspace of equal length.
			xl3 = np.linspace(0, 1, abs(el3_cut))
			xl3_arctan = np.linspace(-10, 10, abs(el3_cut))

			#make a step function using the linspace created.
			
			#voight or a tangent function
			if args.fit_function =="Voight":
			
				y = smoothstep(xl3, N=4)

				
			elif args.fit_function == "Arctan":
			
				y = np.arctan(xl3_arctan)
				y = y - min(y)
				y = y / max(y)


			
			#1-- Identifies the average intensity post step_stop and the intensity at step_start. 
			#2-- Average the parallel and antiparallel spectra finding difference between average post step_stop and min post (L2 peak, pre step_stop)
			#-- Using this we take difference in intensitys of 1 and subtract 2 to get step height.
			#-- The step start is then shifted to intensity at step_start.
			
			

			#(mean intensity post step stop - step_start intensity) - (average spectra post step stop - minima post l2 peak) 
			absorption_difference =  loc_absorption[i][edge] - loc_absorption[i][step_start_energy] 
			
			#transpose the step to intensity at step start energy.
			l3_transpose = (loc_absorption[i][edge])
			
		
			
			y =   -y * absorption_difference

				
			#create zeros up to L3 step
			pre = zerolistmaker(len(loc_absorption[i][:step_stop_energy]))
			
			#concatenate
			pre_plus_l3 = np.concatenate([pre, y])
			
			#post region
			post = zerolistmaker(len(loc_absorption[i][step_start_energy:])) + pre_plus_l3[-1]
			
			#concatenate
			total = np.concatenate([pre_plus_l3, post])
			
			
			total = total + l3_transpose
			
            

            
            
            
		elif args.apply_step == "off":
        
			#subtracted_step = loc_absorption[i]
			#stepfunction = np.zeros(len(loc_energy[i]))
			total = np.zeros(len(loc_energy[i]))	
			
		post_step = loc_absorption[i] - total
		
		step.append(total)
		subtracted_step.append(post_step)
		
		
    
	return step, subtracted_step"""


def smoothstep(x, x_min=0, x_max=1, N=3):
    x = np.clip((x - x_min) / (x_max - x_min), 0, 1)
    result = 0
    for n in range(0, N + 1):
        result += comb(N + n, n) * comb(2 * N + 1, N - n) * (-x) ** n

    result *= x ** (N + 1)
    return result


def single_step(energy, absorption, args):

    loc_energy = energy
    loc_absorption = absorption

    if len(np.array(loc_absorption).shape) > 1:
        n_files = len(np.array(loc_absorption))
    else:
        n_files = 1

    step = []
    subtracted_step = []

    for i in range(n_files):

        if args.step_stop and args.step_start and args.edge:

            if args.apply_step == "on":
                # dummy variables

                # find array point

                step_stop_energy = find_array_equivalent(loc_energy[i], args.step_stop)
                step_start_energy = find_array_equivalent(
                    loc_energy[i], args.step_start
                )
                edge = find_array_equivalent(loc_energy[i], args.edge)

                el3_cut = step_start_energy - step_stop_energy

                # create a linspace of equal length.
                xl3 = np.linspace(0, 1, abs(el3_cut))
                xl3_arctan = np.linspace(-10, 10, abs(el3_cut))

                # make a step function using the linspace created.

                # voight or a tangent function
                if args.fit_function == "Voight":

                    y = smoothstep(xl3, N=4)

                elif args.fit_function == "Arctan":

                    y = np.arctan(xl3_arctan)
                    y = y - min(y)
                    y = y / max(y)

                """
				1-- Identifies the average intensity post step_stop and the intensity at step_start. 
				2-- Average the parallel and antiparallel spectra finding difference between average post step_stop and min post (L2 peak, pre step_stop)
				-- Using this we take difference in intensitys of 1 and subtract 2 to get step height.
				-- The step start is then shifted to intensity at step_start.
				
				 """

                # (mean intensity post step stop - step_start intensity) - (average spectra post step stop - minima post l2 peak)
                absorption_difference = (
                    loc_absorption[i][edge] - loc_absorption[i][step_start_energy]
                )

                # transpose the step to intensity at step start energy.
                l3_transpose = loc_absorption[i][edge]

                y = y * absorption_difference

                # create zeros up to L3 step
                pre = zerolistmaker(len(loc_absorption[i][:step_start_energy]))

                # concatenate
                pre_plus_l3 = np.concatenate([pre, y])

                # post region
                post = (
                    zerolistmaker(len(loc_absorption[i][step_stop_energy:]))
                    + pre_plus_l3[-1]
                )

                # concatenate
                total = np.concatenate([pre_plus_l3, post])

                # total = total + l3_transpose
                total = total - total[0]

            elif args.apply_step == "off":

                # subtracted_step = loc_absorption[i]
                # stepfunction = np.zeros(len(loc_energy[i]))
                total = np.zeros(len(loc_energy[i]))
        else:
            total = np.zeros(len(loc_energy[i]))

        post_step = loc_absorption[i] - total

        step.append(total)
        subtracted_step.append(post_step)

    return step, subtracted_step
