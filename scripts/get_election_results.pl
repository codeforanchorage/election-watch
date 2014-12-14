#!/usr/bin/perl

use strict;
use DB_File;

my $DATA_DIRECTORY = "/var/tmp/";

# Grab the data from the Division of Elections using a text mode web browser
open IN, "lynx -dump 'http://www.elections.alaska.gov/results/14GENR/data/results.htm' |";

# Open an output file for text messages
open OUT, ">texts.txt";

# Strip off some headers.
# Note: These are not currently used for anything and can be renamed as required.
my $ln_header1 = <IN>;
my $ln_header2 = <IN>;
my $ln_header3 = <IN>;
my $ln_header4 = <IN>;
my $ln_header5 = <IN>;
my $ln_header6 = <IN>;
my $ln_header7 = <IN>;
my $ln_header8 = <IN>;
my $ln_header9 = <IN>;
my $ln_header10 = <IN>;

# Get the lock on the database
dblock();

# Open the database
my %races;
dbmopen(%races, "$DATA_DIRECTORY/races", 0666);
my %results;
dbmopen(%results, "$DATA_DIRECTORY/results", 0666);

# Open the numbers hashtable
# Contains: Subscriber phone number => list of subscribed races
my %numbers;
dbmopen(%numbers, "$DATA_DIRECTORY/numbers", 0666);

# Read in the entire numbers hashtable and split/reverse it to race => number
# so we can look up subscribers by race
my %racenumbers;  # contains race => @subscriber_list pairs
foreach my $number (keys %numbers)
{
	my $racestring = $numbers{$number};
	my @racelist = split /,/, $racestring;
	foreach my $race (@racelist)
	{
		unless($racenumbers{$race})
		{
			$racenumbers{$race} = [];
		}
		print STDERR "$race => $number\n";
		push @{$racenumbers{$race}}, $number;
	}
}

# Loop through all the races to the end of the page
while(my $ln_race = <IN>)
{
	my $ln_total = <IN>;
	my $ln_precincts = <IN>;
	my $ln_reporting = <IN>;
	my $ln_timescounted = <IN>;
	my $ln_totalvotes = <IN>;
	my $ln_line = <IN>;
	my $ln_filler = <IN>;

	# Parse race name
	my $race = $ln_race;
	# Remove trailing newline and leading/trailing whitespace
	chomp $race;
	$race =~ s/^ +//;
	$race =~ s/ +$//g;

	# Parse total precinct count
	$ln_precincts =~ m/([0-9]+)/;
	my $precincts = $1;

	# Parse precinct reporting count
	$ln_reporting =~ m/([0-9]+) ([0-9.]+)/;
	my $reporting = $1;
	my $pct_reporting = $2;

#	print STDERR "found race: $race $precincts/$reporting ($pct_reporting\%)\n";

	# Check to see if the race has been updated
	my $racestring = "$precincts $reporting $pct_reporting";
	my $should_update_race; # boolean flag stating whether race updated
	my $text;
	if($racestring ne $races{$race})
	{
		$races{$race} = $racestring;
		$should_update_race = 1;
	}
	else
	{
		$should_update_race = 0;
	}

	# Parse the rest of the race and prepare a short report
	# This step is performed even if the race has not been updated
	my $racetext = ""; # a short report on the race
	for(;;)
	{
		my $ln_res = <IN>;
		my $t = $ln_res;
		chomp $t;
		$t =~ s/ +$//;
		$t =~ s/^ +//;
		if("$t" eq "") { last; }
		$t =~ m/^(.*?) ?([A-Z]{0,3}) ([0-9]+) ([0-9.]+).$/;
		my $candidate = $1;
		my $party = $2;
		my $count = $3;
		my $percentage = $4;
		my $lname = $candidate;
		$lname =~ s/[, ].*//;
#		last if($candidate =~ m/MEASURE/);
#		print STDERR "found candidate: $race\t$candidate\t$party\t$count\t$percentage\n";
		if($should_update_race)
		{
			# Update the race hashtable
			my $racekey = "$race-$candidate-$party";
			my $raceval = "$percentage-$count";
			$results{$racekey} = $raceval;
		}

		$racetext .= "$lname $party $percentage\%\n";
	}
	chomp $racetext;

	# If the race has been updated, broadcast the report
	if($should_update_race)
	{
		$racetext = "Election Watch\n$race\n($reporting/$precincts)\n$racetext";
#		print "$racetext\n###\n\n";
		if($racenumbers{$race})
		{
			for my $num (@{$racenumbers{$race}})
			{
				print "$num\n$racetext\n###\n";
				print OUT "$num\n$racetext\n###\n";
			}
		}
	}
}

dbmclose %races;
dbmclose %results;
dbmclose %numbers;
dbunlock();

sub dblock
{
        # make 15 attempts to get the lock before going ahead anyway
        for(my $ct = 0; $ct < 15; $ct++)
        {
                my $test = mkdir "/var/tmp/dblock";
                last if($test);
                sleep 1;
        }
}

sub dbunlock
{
        rmdir "/var/tmp/dblock";
}

