import { Component, OnInit } from '@angular/core';
import { RewardService } from '../rewards/reward.service'
import {Router, ActivatedRoute, Params} from '@angular/router';

@Component({
  selector: 'app-rewards',
  templateUrl: './rewards.component.html',
  styleUrls: ['./rewards.component.css']
})
export class RewardsComponent implements OnInit {

  twitterData : any;
  tweetId;
  tweetDate;
  constructor(private rewardService : RewardService, private activatedRoute: ActivatedRoute) { }

  ngOnInit(): void {
    this.activatedRoute.queryParams.subscribe(params => {
      this.tweetId = params['tweetID'];
      if(this.tweetId != null)
      {
        this.getData(this.tweetId);
        console.log(this.tweetId);
      }
    });

  }
    
  getData(tweetId: string){
    this.tweetId = tweetId;
    this.rewardService.getRewardsDetails(tweetId).subscribe(tData => {
      this.twitterData = tData;
    });
    this.rewardService.getTweetDate(this.tweetId).subscribe(data => {
      this.tweetDate = data[0]['tweet_date'];
    });
  } 

  downloadFile() {
    const replacer = (key, value) => (value === null ? '' : value); // specify how you want to handle null values here
    var csvArray = "from,to,amount,from-shard,to-shard,passphrase-file,passphrase-string,gas-price\n";
    for(var i=0;i<this.twitterData.length;i++)
    {
      var to_address = this.twitterData[i]['angel_one_address'];
      var amount = (Math.round(this.twitterData[i]['reward'] * 100) / 100).toFixed(2);;
      csvArray = csvArray + "one1nskypwzgmh7ufud7ep0j4pyd2rvwwh0ukrvp77,"+to_address+","+amount+",0,0,,harmonaut,\n";
    }
  
    const a = document.createElement('a');
    const blob = new Blob([csvArray], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
  
    a.href = url;
    a.download = this.tweetDate + '-angelrewards.csv';
    a.click();
    window.URL.revokeObjectURL(url);
    a.remove();
  }
  
}
