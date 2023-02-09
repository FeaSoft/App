! Description:
! Definition of an element index set.
module m_eset
    implicit none
    
    private
    public t_eset, new_eset
    
    type t_eset
        integer              :: n_elements    ! number of element indices
        integer, allocatable :: i_elements(:) ! index of elements
    contains
        final :: destructor
    end type
    
    interface new_eset
        module procedure :: constructor
    end interface
    
    contains
    
    ! Description:
    ! Element index set constructor.
    type(t_eset) function constructor(n_elements) result(self)
        integer, intent(in) :: n_elements ! number of element indices
        self%n_elements = n_elements
        allocate(self%i_elements(self%n_elements))
    end function
    
    ! Description:
    ! Element index set destructor.
    subroutine destructor(self)
        type(t_eset), intent(inout) :: self
        if (allocated(self%i_elements)) deallocate(self%i_elements)
    end subroutine
    
end module
