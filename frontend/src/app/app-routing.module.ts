import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { RewardsComponent } from './rewards/rewards.component';

const routes: Routes = [
  {path: 'rewards', component: RewardsComponent}
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
