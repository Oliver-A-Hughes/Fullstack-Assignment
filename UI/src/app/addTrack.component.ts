import { Component } from "@angular/core";
import { FormBuilder, Validators } from "@angular/forms";
import { WebService } from "./web.service";


@Component({
    selector: 'addTrack',
    templateUrl: './addTrack.component.html',
    styleUrls: ['./addTrack.component.css']
})

export class addTrackComponent {
    constructor(private webService: WebService,
        private formBuilder: FormBuilder) {}
    
    trackForm;
    trackTypes:Array<Object> = [
        {name: "Circuit"},
        {name: "Oval"},
        {name: "Street"}
    ];

    ngOnInit(){
            this.getForm()
        }

    getForm(){
        this.trackForm = this.formBuilder.group({
            trackName: ['', Validators.required],
            location: ['', Validators.required],
            country: ['', Validators.required],
            type: ['',Validators.required],
            turns: ['', Validators.required],
            length: ['', Validators.required], 
            imageURL: ['', Validators.required]
                });
    }
    
    onSubmit(){
        this.webService.postTrack(this.trackForm.value)
        this.trackForm.reset()
        }

    isInvalid(control) {
        return this.trackForm.controls[control].invalid &&
                this.trackForm.controls[control].touched;
            }
            
    isUnTouched() {
        return this.trackForm.controls.trackName.pristine ||
               this.trackForm.controls.location.pristine ||
               this.trackForm.controls.country.pristine ||
               this.trackForm.controls.type.pristine ||
               this.trackForm.controls.turns.pristine ||
               this.trackForm.controls.length.pristine ||
               this.trackForm.controls.imageURL.pristine;
            }
        
    
    isIncomplete() {    
        return this.isInvalid('trackName') ||
                this.isInvalid('location') ||
                this.isInvalid('country') ||
                this.isInvalid('type') ||
                this.isInvalid('turns') ||
                this.isInvalid('length') ||
                this.isInvalid('imageURL') ||
                this.isUnTouched();
            
        }
    

    }