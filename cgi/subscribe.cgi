#!/usr/bin/perl

use CGI;
use strict;
use DB_File;
use Captcha::reCAPTCHA;

open STDERR, ">&STDOUT";

my $DATA_DIRECTORY = "/var/tmp/";

my $cgi = CGI->new;
my $captcha = Captcha::reCAPTCHA->new;

sanitize($cgi);

print $cgi->header, $cgi->start_html(-title=>"Subscribe to Election Alerts",style=>{src=>'/styles.css'});


print <<EOF;
<style>
#recaptcha_area
{
 margin:0 auto !important;
}

#formtable
{
 margin-left: auto;
 margin-right: auto;
 width: 560px;
}

#formtable tr td
{
 text-align: left;
 vertical-align: top;
}
</style>

EOF

print "<a href='http://alaskaelectionwatch.com'><img src='/electionwatch.png' class='logo'></img></a><br/>";

my $phone = $cgi->param("phone");
if("$phone" ne "")
{
	# validate phone number
        my $nk = $phone;
        $nk =~ s/[^0-9]//g;
        $nk =~ s/^[01]*//;
        if(length $nk < 10)
        {
                $nk = "907$nk";
        }
        if(length $nk != 10)
        {
#		print "phone number $phone is invalid\n";
        }
	else
	{
		$phone = $nk;
	}

	# validate captcha
	my $challenge = $cgi->param("recaptcha_challenge_field");
	my $response = $cgi->param("recaptcha_response_field");
	my $captcha_result = $captcha->check_answer("6LdbsPwSAAAAALVt2jirU2zo4ioD2OShYSLScBFB",  $ENV{'REMOTE_ADDR'}, $challenge, $response);
#	foreach my $k (sort keys %ENV)
#	{
#		print "$k = ", $ENV{$k}, "<br/>";
#	}
#	if($captcha_result->{is_valid})
	if(1 && length($nk) == 10)
	{
		my @races = $cgi->multi_param('races');
		my $racestring = join ",", @races;
		my %numbers;
		my %races;
		my %results;
		dblock();
		dbmopen(%numbers, "$DATA_DIRECTORY/numbers", 0666);
		dbmopen(%results, "$DATA_DIRECTORY/results", 0666);
		dbmopen(%races, "$DATA_DIRECTORY/races", 0666);
		$numbers{$phone} = $racestring;
		print "You have been subscribed to the following election alerts:<br/>";
		print "<ul>\n";
		foreach my $r (@races)
		{
			print "<li>$r</li>\n";
		}
	
		print "</ul>\n";
		dbmclose %races;
		dbmclose %results;
		dbmclose %numbers;
		dbunlock();
	}
	else
	{
#		print "problem with captcha... ", $captcha_result->{error}, "<br/>";
		print "problem with phone number $phone<br/>";
	}	
	
}
else
{
	
	my %races;
	dblock();
	dbmopen(%races,"$DATA_DIRECTORY/races", 0666);
	my @r = sort keys %races;

        print "<p><i>This site allows you to subscribe your mobile device to receive updates for";
        print "<br>the Alaska state and local elections you would like to track. On election";
        print "<br>night we will send texts whenever the <a target='_blank' href='http://www.elections.alaska.gov/results/14GENR/data/results.htm'>State Election web site</a> is updated.";
        print "</i><p><p>";
	
	print $cgi->start_form;

	print "<table id='formtable'>";
	
	print "<tr><td>Enter your phone number:</td><td>";
	
	print $cgi->textfield("phone");
	
	print "</td></tr>";
	
	print "<tr><td>Choose the races for which you want to receive alerts:</td><td>";
	
	print $cgi->scrolling_list(-name=>"races", -values=>\@r, -size=>8, -multiple=>'true');

	print "</td></tr>";

#`	print "<tr><td>Prove you are human:</td><td>";

#	print $captcha->get_html('6LdbsPwSAAAAABhFQDwaZgFTPfkZSWviw9DQ2hel');

	
	print "<tr><td>&nbsp;</td><td>";
        print $cgi->submit;

	print "</td></tr>";

        print "</table>";

        print "<p>Each time you use this form your previous choices are replaced.";

        print "<p>Having a problem? <a href='mailto:election_help\@biofidelic.com?subject=AlaskaElectionWatch'>Send us a message</a>";

	print $cgi->end_form;
	
	print $cgi->end_html;

	dbmclose %races;
	dbunlock();
	
	
}

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


sub sanitize
{
	my $cgi = shift;

	my @params = $cgi->param();

	my %valid_params = (
		"phone" => 1,
		"recaptcha_challenge_field" => 1,
		"recaptcha_response_field" => 1
	);

	my %valid_multi_params = (
		"races" => 1
	);

	foreach my $p (@params)
	{
		if($valid_params{$p})
		{
			$cgi->param($p, encode_entities($cgi->param($p)));
		}
		elsif($valid_multi_params{$p})
		{
			my @a = $cgi->multi_param($p);
			my @b;
			foreach my $x (@a)
			{
				push @b, encode_entities($x);
			}
			$cgi->multi_param($p, @b);
		}
		else
		{
			$cgi->param($p, undef);
		}
		
	}

}
