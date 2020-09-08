import { Component, OnInit } from '@angular/core';
import { RewardService } from '../rewards/reward.service'
import {Router, ActivatedRoute, Params} from '@angular/router';

@Component({
  selector: 'app-rewards',
  templateUrl: './rewards.component.html',
  styleUrls: ['./rewards.component.css']
})
export class RewardsComponent implements OnInit {

  twitterData;
  tweetId;
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
      console.log(tData);
      this.twitterData = tData;
    })
  }
}
