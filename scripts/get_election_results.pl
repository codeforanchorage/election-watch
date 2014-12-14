#!/usr/bin/perl

use strict;
use DB_File;

my $DATA_DIRECTORY = "/var/tmp/";

open IN, "lynx -dump 'http://www.elections.alaska.gov/results/14GENR/data/results.htm' |";
#open IN, "lynx -width=320 -dump 'http://localhost/results.htm' |";
open OUT, ">texts.txt";

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

dblock();
my %races;
dbmopen(%races, "$DATA_DIRECTORY/races", 0666);
my %results;
dbmopen(%results, "$DATA_DIRECTORY/results", 0666);
my %numbers;
dbmopen(%numbers, "$DATA_DIRECTORY/numbers", 0666);

my %racenumbers;
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

while(my $ln_race = <IN>)
{
	my $ln_total = <IN>;
	my $ln_precincts = <IN>;
	my $ln_reporting = <IN>;
	my $ln_timescounted = <IN>;
	my $ln_totalvotes = <IN>;
	my $ln_line = <IN>;
	my $ln_filler = <IN>;

	my $race = $ln_race;
	chomp $race;
	$race =~ s/^ +//;
	$race =~ s/ +$//g;

	$ln_precincts =~ m/([0-9]+)/;
	my $precincts = $1;

	$ln_reporting =~ m/([0-9]+) ([0-9.]+)/;
	my $reporting = $1;
	my $pct_reporting = $2;

	print "found race: $race $precincts/$reporting ($pct_reporting\%)\n";
	my $racestring = "$precincts $reporting $pct_reporting";
	my $should_update_race;
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

	my $racetext = "";
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
#		print "found candidate: $race\t$candidate\t$party\t$count\t$percentage\n";
		if($should_update_race)
		{
			my $racekey = "$race-$candidate-$party";
			my $raceval = "$percentage-$count";
			$results{$racekey} = $raceval;
		}
		$racetext .= "$lname $party $percentage\%\n";
	}
	chomp $racetext;
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

