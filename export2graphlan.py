#!/usr/bin/env python

from argparse import ArgumentParser
from colorsys import hsv_to_rgb
from math import log
from hclust2.hclust2 import DataMatrix


__author__ = 'Francesco Asnicar'
__email__ = "francesco.asnicar@gmail.com"
__version__ = '0.09'
__date__ = '7th July 2014'


def scale_color((h, s, v), factor = 1.) :
	if (h < 0.) or (h > 360.) :
		raise Exception(' '.join(['[scale_color()] Hue value out of range (0, 360):', str(h)]))
	
	if (s < 0.) or (s > 100.) :
		raise Exception(' '.join(['[scale_color()] Saturation value out of range (0, 100):', str(s)]))

	if (v < 0.) or (v > 100.) :
		raise Exception(' '.join(['[scale_color()] Value value out of range (0, 100):', str(v)]))

	if (factor < 0.) or (factor > 1.) :
		raise Exception(' '.join(['[scale_color()] Factor value out of range (0.0, 1.0):', str(factor)]))

	v *= factor
	r, g, b = hsv_to_rgb(h / 360., s / 100., v / 100.)
	return '#{0:02x}{1:02x}{2:02x}'.format(int(round(r * 255.)), int(round(g * 255.)), int(round(b * 255.)))


def read_params() :
	parser = ArgumentParser(description =  "export2graphlan.py (ver. " + __version__ +
		" of " + __date__ + "). Convert MetaPhlAn, LEfSe, and/or HUMAnN output to GraPhlAn input format. Authors: "
		+ __author__ + " (" + __email__ + ")")
	
	# input parameters group
	group = parser.add_argument_group(title = 'input parameters',
		description = "You need to provide at least one of the two arguments")
	group.add_argument('-i', '--lefse_input',
		type = str,
		required = False,
		help = "LEfSe input data")
	group.add_argument('-o', '--lefse_output',
		type = str,
		required = False,
		help = "LEfSe output result data")

	# output parameters group
	group = parser.add_argument_group(title = 'output parameters')
	group.add_argument('-t', '--tree',
		type = str,
		required = True,
		help = "Output filename where save the input tree for GraPhlAn")
	group.add_argument('-a', '--annotation',
		type = str,
		required = True,
		help = "Output filename where save GraPhlAn annotation")

	# annotations
	parser.add_argument('--annotations',
		default = None,
		type = str,
		required = False,
		help = "List which levels should be annotated in the tree. Use a comma separate values form, e.g., --annotation_levels 1,2,3")
	parser.add_argument('--external_annotations',
		default = None,
		type = str,
		required = False,
		help = "List which levels should use the external legend for the annotation. Use a comma separate values form, e.g., --annotation_levels 1,2,3")
	# shaded background
	parser.add_argument('--background',
		default = None,
		type = str,
		required = False,
		help = "List which levels should be highlight with a shaded background. Use a comma separate values form, e.g., --background 1,2,3")
	# title
	parser.add_argument('--title',
		type = str,
		required = False,
		help = "If specified set the title of the GraPhlAn plot. Surround the string with \" if it contains spaces, e.g., --title \"Title example\"")
	# title font size
	parser.add_argument('--title_font_size',
		default = 15,
		type = int,
		required = False,
		help = "Set the title font size. Default is 15")
	# clade size
	parser.add_argument('--def_clade_size',
		default = 10.,
		type = float,
		required = False,
		help = "Set a default size for clades that are not found as biomarkers by LEfSe. Default is 10")
	parser.add_argument('--min_clade_size',
		default = 20.,
		type = float,
		required = False,
		help = "Set the minimum value of clades that are biomarkers. Default is 20")
	parser.add_argument('--max_clade_size',
		default = 200.,
		type = float,
		required = False,
		help = "Set the maximum value of clades that are biomarkers. Default is 200")
	# font size
	parser.add_argument('--def_font_size',
		default = 10,
		type = int,
		required = False,
		help = "Set a default font size. Default is 10")
	parser.add_argument('--min_font_size',
		default = 8,
		type = int,
		required = False,
		help = "Set the minimum font size to use. Default is 8")
	parser.add_argument('--max_font_size',
		default = 12,
		type = int,
		required = False,
		help = "Set the maximum font size. Default is 12")
	# legend font size
	parser.add_argument('--annotation_legend_font_size',
		default = 10,
		type = int,
		required = False,
		help = "Set the font size for the annotation legend. Default is 10")
	# abundance threshold
	parser.add_argument('--abundance_threshold',
		default = 20.,
		type = float,
		required = False,
		help = "Set the minimun abundace value for a clade to be annotated. Default is 20.0")

	DataMatrix.input_parameters(parser)
	args = parser.parse_args()

	# check if at least one of the input params is given
	if (not args.lefse_input) and (not args.lefse_output) :
		raise Exception("[read_params()] You must provide at least one of the two input parameters: ")

	# check that min_clade_size is less than max_clade_size
	if args.min_clade_size > args.max_clade_size :
		print "[W] min_clade_size cannot be greater than max_clade_size, assigning their default values"
		args.min_clade_size = 20.
		args.max_clade_size = 200.
	
	# check that min_font_size is less than max_font_size
	if args.min_font_size > args.max_font_size :
		print "[W] min_font_size cannot be greater than max_font_size, assigning their default values"
		args.min_font_size = 8
		args.max_font_size = 12
	
	return args


def main() :
	colors = [(245, 90., 100.), (125, 80., 80.), (0, 80., 100.), (195, 100., 100.), (150, 100., 100.),
		(55, 100., 100.), (280, 80., 88.)] # HSV format
	args = read_params()
	lefse_input = None
	lefse_output = {}
	color = {}
	biomarkers = set()
	taxa = []
	abundances = {}
	max_abundances = None
	max_effect_size = None
	max_log_effect_size = None
	background_list = []
	shaded_background = []
	annotations_list = []
	external_annotations_list = []

	# get the levels that should be shaded
	if args.background :
		background_list = [int(i.strip()) for i in args.background.strip().split(',')]

	# get the levels that will use the internal annotation
	if args.annotations :
		annotations_list = [int(i.strip()) for i in args.annotations.strip().split(',')]

	# get the levels that will use the external legend annotation
	if args.external_annotations :
		external_annotations_list = [int(i.strip()) for i in args.external_annotations.strip().split(',')]

	# read the LEfSe files
	try :
		if args.lefse_input :
			lefse_input = DataMatrix(args.lefse_input, args)
			taxa = [t.replace('|', '.') for t in lefse_input.get_fnames()] # build taxonomy list
			abundances = dict(lefse_input.get_averages())
			max_abundances = max([abundances[x] for x in abundances])

		if args.lefse_output :
			lst = []

			with open(args.lefse_output, 'r') as out_file :
				for line in out_file :
					t, v1, bk, es, pv = line.strip().split('\t')
					lefse_output[t] = (es, bk, v1, pv)

					# get distinct biomarkers
					if bk :
						biomarkers |= set([bk])

					# get all effect size
					if es :
						lst.append(float(es))

				max_effect_size = max(lst)

			# no lefse_input file provided!
			if not taxa :
				# build taxonomy list
				for t in lefse_output :
					taxa.append(t)

			if not abundances :
				# build abundaces map
				pass
#		else :
			# get biomarkers from lefse_input
#			with open(args.lefse_input, 'r') as in_file :
#				for bk in in_file.readline().strip().split('\t')[1:] :
#					biomarkers |= set([bk])
	except Exception as e :
		print e

	# write the tree
	try :
		with open(args.tree, 'w') as tree_file :
			for taxonomy in taxa :
				tree_file.write(''.join([taxonomy, '\n']))
	except Exception as e :
		print e

	# for each biomarker assign it to a different color
	i = 0
	for bk in biomarkers :
		color[bk] = i % len(colors)
		i += 1

	# find max log abs value of effect size
	if lefse_output :
		lst = []

		for t in lefse_output :
			es, _, _, _ = lefse_output[t]
			
			if es :
				lst.append(abs(log(float(es) / max_effect_size)))

		max_log_effect_size = max(lst)

	# write the annotation
	try :
		with open(args.annotation, 'w') as annot_file :
			# set the title
			if args.title :
				annot_file.write(''.join(['\t'.join(['title', args.title]), '\n']))
				annot_file.write(''.join(['\t'.join(['title_font_size', str(args.title_font_size)]), '\n']))

			# write some basic customizations
			annot_file.write(''.join(['\t'.join(['clade_separation', '0.5']), '\n']))
			annot_file.write(''.join(['\t'.join(['branch_bracket_depth', '0.65']), '\n']))
			annot_file.write(''.join(['\t'.join(['branch_bracket_width', '0.5']), '\n']))
			annot_file.write(''.join(['\t'.join(['annotation_legend_font_size', str(args.annotation_legend_font_size)]), '\n']))
			annot_file.write(''.join(['\t'.join(['class_legend_font_size', '10']), '\n']))
			annot_file.write(''.join(['\t'.join(['class_legend_marker_size', '1.5']), '\n']))

			# write the biomarkers' legend
			for bk in biomarkers :
				biom = bk.replace('_', ' ')
				rgb = scale_color(colors[color[bk]])
				annot_file.write(''.join(['\t'.join([biom, 'annotation', biom]), '\n']))
				annot_file.write(''.join(['\t'.join([biom, 'clade_marker_color', rgb]), '\n']))
				annot_file.write(''.join(['\t'.join([biom, 'clade_marker_size', '45']), '\n']))

			# write the annotation for the tree
			for taxonomy in taxa :
				level = taxonomy.count('.') + 1 # which level is this taxonomy?
				clean_taxonomy = taxonomy[taxonomy.rfind('.') + 1:] # retrieve the last level in taxonomy
				scaled = args.def_clade_size

				# scaled the size of the clade by the average abundance
				if taxonomy.replace('.', '|') in abundances :
					scaled = args.min_clade_size + args.max_clade_size * log(1. + (abundances[taxonomy.replace('.', '|')] / max_abundances))
				
				annot_file.write(''.join(['\t'.join([clean_taxonomy, 'clade_marker_size', str(scaled)]), '\n']))

				# 
				for l in background_list :
					if level >= l :
						lst = [s.strip() for s in taxonomy.strip().split('.')]
						t = '.'.join(lst[:l])

						if t not in shaded_background :
							shaded_background.append(t)

							font_size = args.min_font_size + ((args.max_font_size - args.min_font_size) / l)

							annot_file.write(''.join(['\t'.join([t, 'annotation_background_color', '#a0a0a0']), '\n']))
							annot_file.write(''.join(['\t'.join([t, 'annotation', '*']), '\n']))
							annot_file.write(''.join(['\t'.join([t, 'annotation_font_size', str(font_size)]), '\n']))

				if lefse_output :
					if taxonomy in lefse_output :
						es, bk, _, _ = lefse_output[taxonomy]

						# if it is a biomarker then color and label it!
						if bk :
							fac = abs(log(float(es) / max_effect_size)) / max_log_effect_size
							
							try :
								rgbs = scale_color(colors[color[bk]], fac)
								annot_file.write(''.join(['\t'.join([clean_taxonomy, 'clade_marker_color', rgbs]), '\n']))

								if (level in annotations_list) or (level in external_annotations_list) :
									font_size = args.min_font_size + ((args.max_font_size - args.min_font_size) / level)
									annotation = '*' if level in annotations_list else '*:*'

									# write the annotation only if the abundance is above a given threshold
									if scaled >= args.abundance_threshold :
										annot_file.write(''.join(['\t'.join([clean_taxonomy, 'annotation_background_color', rgbs]), '\n']))
										annot_file.write(''.join(['\t'.join([clean_taxonomy, 'annotation', annotation]), '\n']))
										annot_file.write(''.join(['\t'.join([clean_taxonomy, 'annotation_font_size', str(font_size)]), '\n']))
									else : # the clade abundance is lower w.r.t the threshold
										pass
								else : # the taxonomy level is less that the min of the annotation list
									pass
							except Exception as e :
								print e
						else : # it's not a biomarker
							pass
				else : # lefse.output not provided
					pass
	except Exception as e :
		print e


if __name__ == '__main__' :
	main()
