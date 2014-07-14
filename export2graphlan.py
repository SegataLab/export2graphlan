#!/usr/bin/env python

from argparse import ArgumentParser
from colorsys import hsv_to_rgb
from math import log
from hclust2.hclust2 import DataMatrix
from biom import load_table
from random import randrange
from os import remove


__author__ = 'Francesco Asnicar'
__email__ = "francesco.asnicar@gmail.com"
__version__ = '0.10'
__date__ = '11th July 2014'


def scale_color((h, s, v), factor = 1.) :
	"""
	Takes as input a tuple that represents a color in HSV format, and optionally a scale factor.
	Return an RGB string that is the converted HSV color, scaled by the given factor.
	"""
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
	"""
	Parse the input parameters, performing some validity check.
	Return the parsed arguments.
	"""
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
		help = "List which levels should be annotated in the tree. Use a comma separate values form, e.g., --annotation_levels 1,2,3. Default is None")
	parser.add_argument('--external_annotations',
		default = None,
		type = str,
		required = False,
		help = "List which levels should use the external legend for the annotation. Use a comma separate values form, e.g., --annotation_levels 1,2,3. Default is None")
	# shaded background
	parser.add_argument('--background_levels',
		default = None,
		type = str,
		required = False,
		help = "List which levels should be highlight with a shaded background. Use a comma separate values form, e.g., --background_levels 1,2,3")
	parser.add_argument('--background_clades',
		default = None,
		type = str,
		required = False,
		help = "Specify the file that contains clades that should be highlight with a shaded background. Write one clades per row in the file")
	parser.add_argument('--background_colors',
		default = None,
		type = str,
		required = False,
		help = "Set the color in RGB format to use for the shaded background. Can be either a file (that contains for each row one color) or direct specified as a string (comma-separate-values). Colors can be either in RGB or HSV format")
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
	# ONLY lefse_input provided
	parser.add_argument('--most_abundant',
		default = 10,
		type = int,
		required = False,
		help = "When only lefse_input is provided, you can specify how many clades highlight. Since the biomarkers are missing, they will be chosen from the most abundant")
	parser.add_argument('--least_biomarkers',
		default = 3,
		type = int,
		required = False,
		help = "When only lefse_input is provided, you can specify the minimum number of biomarkers extract. The taxonomy is parsed, and the level is choosen in order to have at least the specified number of biomarkers")

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


def get_file_type(filename) :
	"""
	Return the extension (if any) of the ``filename`` in lower case.
	"""
	return filename[filename.rfind('.') + 1:].lower()


def parse_biom(filename) :
	"""
	"""
	biom_table = load_table(filename)
	strs = biom_table.delimited_self(header_value = 'TAXA', header_key = 'taxonomy')
	lst1 = [s for s in strs.split('\n')]
	lst1 = lst1[1:] # skip the "# Constructed from biom file" entry
	biom_file = 'biom_' + str(randrange(999999)) + '.txt'

	with open(biom_file, 'w') as f :
		for l in lst1 :
			lst = [s for s in l.split('\t')]
			lst = lst[1:] # skip the OTU ids

			# Clean an move taxa in first place
			taxa = '.'.join( [ s.strip().replace('[', '').replace('\'', '').replace(']', '') for s in lst[-1].split(',') ] )
			lst = [taxa] + lst[:-1]

			f.write('\t'.join(lst))

	return biom_file


def get_most_abundant(abundances, xxx) :
	"""
	Sort by the abundance level all the taxonomy that represent at least two levels.
	Return the first ``xxx`` most abundant.
	"""
	abundant = []

	for a in abundances :
		if a.count('|') > 0 :
			abundant.append((float(abundances[a]), a.replace('|', '.')))

	abundant.sort(reverse = True)

	return abundant[:xxx]


def get_biomarkes(abundant, xxx) :
	"""
	Split the taxonomy and then look, level by level, when there are at least ``xxx`` distinct branches.
	Return the set of branches as biomarkers to highlight.
	"""
	cc = []
	bk = set()
	lvl = 0

	for _, t in abundant :
		cc.append(t.split('.'))

	while lvl < len(max(cc)) :
		bk = set()

		for c in cc :
			if lvl < len(c) :
				bk |= set([c[lvl]])

		if len(bk) >= xxx :
			break

		lvl += 1

	return bk

def scale_clade_size(minn, maxx, abu, max_abu) :
	"""
	Return the value of ``abu`` scaled to ``max_abu`` logarithmically, and then map from ``minn`` to ``maxx``.
	"""
	return minn + maxx * log(1. + (abu / max_abu))


def main() :
	"""
	"""
	colors = [(245., 90., 100.), (125., 80., 80.), (0., 80., 100.), (195., 100., 100.), (150., 100., 100.), (55., 100., 100.), (280., 80., 88.)] # HSV format
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
	background_clades = []
	background_colors = {}
	annotations_list = []
	external_annotations_list = []

	# get the levels that should be shaded
	if args.background_levels :
		background_list = [int(i.strip()) for i in args.background_levels.strip().split(',')]

	# get the background_clades
	if args.background_clades :
		with open(args.background_clades, 'r') as f:
			background_clades = [str(s.strip()) for s in f]

	# read the set of colors to use for the background_clades
	if args.background_colors :
		col = []

		if get_file_type(args.background_colors) in ['txt'] :
			with open(args.background_colors, 'r') as f :
				col = [str(s.strip()) for s in f]
			pass
		else : # it's a string in csv format
			col = [c.strip() for c in args.background_colors.split(',')]

		lst = {}
		i = 0

		for c in background_clades :
			cc = c[:c.find('.')]

			if cc not in lst :
				background_colors[c] = col[i % len(col)]
				lst[cc] = col[i % len(col)]
				i += 1
			else :
				background_colors[c] = lst[cc]

	# get the levels that will use the internal annotation
	if args.annotations :
		annotations_list = [int(i.strip()) for i in args.annotations.strip().split(',')]

	# get the levels that will use the external legend annotation
	if args.external_annotations :
		external_annotations_list = [int(i.strip()) for i in args.external_annotations.strip().split(',')]

	if args.lefse_input :
		biom_file = None

		# if the lefse_input is in biom format, convert it
		if get_file_type(args.lefse_input) in 'biom' :
			biom_file = parse_biom(args.lefse_input)
			args.lefse_input = biom_file
		
		lefse_input = DataMatrix(args.lefse_input, args)
		taxa = [t.replace('|', '.') for t in lefse_input.get_fnames()] # build taxonomy list
		abundances = dict(lefse_input.get_averages())
		max_abundances = max([abundances[x] for x in abundances])

		# remove the temporary biom file
		if biom_file :
			remove(biom_file)
			print biom_file + ' deleted!'

	if args.lefse_output :
		# if the lefse_output is in biom format... I don't think it's possible!
		if get_file_type(args.lefse_output) in 'biom' :
			print "Really??"

		lst = []

		with open(args.lefse_output, 'r') as out_file :
			for line in out_file :
				t, m, bk, es, pv = line.strip().split('\t')
				lefse_output[t] = (es, bk, m, pv)

				# get distinct biomarkers
				if bk :
					biomarkers |= set([bk])

				# get all effect size
				if es :
					lst.append(float(es))

			max_effect_size = max(lst)

		# no lefse_input file provided!
		if (not taxa) and (not abundances) : # build taxonomy list and abundaces map
			for t in lefse_output :
				_, _, m, _ = lefse_output[t]
				abundances[t.replace('.', '|')] = float(m)

			max_abundances = max([abundances[x] for x in abundances])

			for t in lefse_output :
				scaled = scale_clade_size(args.min_clade_size, args.max_clade_size, abundances[t.replace('.', '|')], max_abundances)

				if scaled >= args.abundance_threshold :
					taxa.append(t)
	else : # no lefse_output provided
		# find the xxx most abundant
		abundant = get_most_abundant(abundances, args.most_abundant)

		# find the highest deeper different taxonomy level with yyy distinct values from the xxx most abundant
		biomarkers = get_biomarkes(abundant, args.least_biomarkers)

		# compose lefse_output variable
		for _, t in abundant :
			b = ''

			for bk in biomarkers :
				if bk in t :
					b = bk

			lefse_output[t] = (2., b, '', '')

		max_effect_size = 1. # It's not gonna working

	# write the tree
	with open(args.tree, 'w') as tree_file :
		for taxonomy in taxa :
			tree_file.write(''.join([taxonomy, '\n']))

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
			annot_file.write(''.join(['\t'.join(['branch_bracket_depth', '0.8']), '\n']))
			annot_file.write(''.join(['\t'.join(['branch_bracket_width', '0.2']), '\n']))
			annot_file.write(''.join(['\t'.join(['annotation_legend_font_size', str(args.annotation_legend_font_size)]), '\n']))
			annot_file.write(''.join(['\t'.join(['class_legend_font_size', '10']), '\n']))
			annot_file.write(''.join(['\t'.join(['class_legend_marker_size', '1.5']), '\n']))

			# write the biomarkers' legend
			for bk in biomarkers :
				biom = bk.replace('_', ' ').upper()
				rgb = scale_color(colors[color[bk]])
				annot_file.write(''.join(['\t'.join([biom, 'annotation', biom]), '\n']))
				annot_file.write(''.join(['\t'.join([biom, 'clade_marker_color', rgb]), '\n']))
				annot_file.write(''.join(['\t'.join([biom, 'clade_marker_size', '40']), '\n']))

			done_clades = []

			# write the annotation for the tree
			for taxonomy in taxa :
				level = taxonomy.count('.') + 1 # which level is this taxonomy?
				clean_taxonomy = taxonomy[taxonomy.rfind('.') + 1:] # retrieve the last level in taxonomy
				scaled = args.def_clade_size

				# scaled the size of the clade by the average abundance
				if taxonomy.replace('.', '|') in abundances :
					scaled = scale_clade_size(args.min_clade_size, args.max_clade_size, abundances[taxonomy.replace('.', '|')], max_abundances)
				
				annot_file.write(''.join(['\t'.join([clean_taxonomy, 'clade_marker_size', str(scaled)]), '\n']))

				# put a bakcground annotation to the levels specified by the user
				shaded_background = []

				for l in background_list :
					if level >= l :
						lst = [s.strip() for s in taxonomy.strip().split('.')]
						t = '.'.join(lst[:l])

						if t not in shaded_background :
							shaded_background.append(t)

							font_size = args.min_font_size + ((args.max_font_size - args.min_font_size) / l)

							annot_file.write(''.join(['\t'.join([t, 'annotation_background_color', args.background_color]), '\n']))
							annot_file.write(''.join(['\t'.join([t, 'annotation', '*']), '\n']))
							annot_file.write(''.join(['\t'.join([t, 'annotation_font_size', str(font_size)]), '\n']))

				# put a bakcground annotation to the clades specified by the user
				for c in background_colors :
					bg_color = background_colors[c]

					if not bg_color.startswith('#') :
						h, s, v = bg_color.split(',')
						bg_color = scale_color((float(h.strip()) , float(s.strip()), float(v.strip())))

					# check if the taxonomy has more than one level
					lvls = [str(cc.strip()) for cc in c.split('.')]

					for l in lvls :
						if (l in taxonomy) and (l not in done_clades) :
							lvl = taxonomy[:taxonomy.index(l)].count('.') + 1
							font_size = args.min_font_size + ((args.max_font_size - args.min_font_size) / lvl)
							

							annot_file.write(''.join(['\t'.join([l, 'annotation_background_color', bg_color]), '\n']))
							annot_file.write(''.join(['\t'.join([l, 'annotation', '*']), '\n']))
							annot_file.write(''.join(['\t'.join([l, 'annotation_font_size', str(font_size)]), '\n']))

							done_clades.append(l)

				if lefse_output :
					if taxonomy in lefse_output :
						es, bk, _, _ = lefse_output[taxonomy]

						# if it is a biomarker then color and label it!
						if bk :
							fac = abs(log(float(es) / max_effect_size)) / max_log_effect_size
							
							try :
								rgbs = scale_color(colors[color[bk]], fac)
							except Exception as e :
								print e
								print ' '.join(["[W] Assign to", taxonomy, "the default color:", colors[color[bk]]])
								rgbs = colors[color[bk]]

							annot_file.write(''.join(['\t'.join([clean_taxonomy, 'clade_marker_color', rgbs]), '\n']))

							# write the annotation only if the abundance is above a given threshold
							if (scaled >= args.abundance_threshold) and ((level in annotations_list) or (level in external_annotations_list)) :
								font_size = args.min_font_size + ((args.max_font_size - args.min_font_size) / level)
								annotation = '*' if level in annotations_list else '*:*'

								annot_file.write(''.join(['\t'.join([clean_taxonomy, 'annotation_background_color', rgbs]), '\n']))
								annot_file.write(''.join(['\t'.join([clean_taxonomy, 'annotation', annotation]), '\n']))
								annot_file.write(''.join(['\t'.join([clean_taxonomy, 'annotation_font_size', str(font_size)]), '\n']))
	except Exception as e :
		print e


if __name__ == '__main__' :
	main()
